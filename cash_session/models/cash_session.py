# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class CashSession(models.Model):
    _name = 'cash.session'
    _order = 'id desc'
    _description = 'Cash Session'

    CASH_SESSION_STATE = [
        ('opening_control', 'Opening Control'),  # method action_cash_session_open
        ('opened', 'In Progress'),               # method action_cash_session_closing_control
        ('closing_control', 'Closing Control'),  # method action_cash_session_close
        ('closed', 'Closed & Posted'),
    ]

    config_id = fields.Many2one('cash.config', string='Cash Config', help="The physical Cash Config you will use.", readonly=True, index=True)
    name = fields.Char(string='Session ID', required=True, readonly=True, default='/')
    user_id = fields.Many2one('res.users', string='Responsible', required=True, index=True, readonly=True, states={'opening_control': [('readonly', False)]}, default=lambda self: self.env.uid)
    currency_id = fields.Many2one(related='config_id.currency_id', string="Currency", readonly=False)
    start_at = fields.Datetime(string='Opening Date', readonly=True)
    stop_at = fields.Datetime(string='Closing Date', readonly=True, copy=False)

    state = fields.Selection(CASH_SESSION_STATE, string='Status', required=True, readonly=True, index=True, copy=False, default='opening_control')

    sequence_number = fields.Integer(string='Order Sequence Number', help='A sequence number that is incremented with each order', default=1)
    login_number = fields.Integer(string='Login Sequence Number', help='A sequence number that is incremented each time a user resumes the cash session', default=0)

    cash_control = fields.Boolean(compute='_compute_cash_all', string='Has Cash Control')
    cash_journal_id = fields.Many2one('account.journal', compute='_compute_cash_all', string='Cash Journal', store=True)
    cash_register_id = fields.Many2one('account.bank.statement', compute='_compute_cash_all', string='Cash Register', store=True)

    cash_register_balance_end_real = fields.Monetary(compute='_compute_cash_all', string="Ending Balance", help="Total of closing cash control lines.")
    cash_register_balance_start = fields.Monetary(compute='_compute_cash_all', string="Starting Balance", help="Total of opening cash control lines.", readonly=True)
    cash_register_total_entry_encoding = fields.Monetary(compute='_compute_cash_all', string='Total Cash Transaction', help="Total of all paid sales orders")
    cash_register_balance_end = fields.Monetary(compute='_compute_cash_all', string="Theoretical Closing Balance", help="Sum of opening balance and transactions.", readonly=True)
    cash_register_difference = fields.Monetary(compute='_compute_cash_all', string='Difference', help="Difference between the theoretical closing balance and the real closing balance.")

    journal_ids = fields.Many2many('account.journal', related='config_id.journal_ids', string='Available Payment Methods')
    order_ids = fields.One2many('account.payment', 'session_id',  string='Orders')
    statement_ids = fields.One2many('account.bank.statement', 'cash_session_id', string='Bank Statement', readonly=True)
    picking_count = fields.Integer(compute='_compute_picking_count')
    rescue = fields.Boolean(string='Recovery Session', help="Auto-generated session for orphan orders, ignored in constraints", readonly=True, copy=False)
    cashbox_lines_ids = fields.One2many('account.cashbox.line', 'cash_session_id', string="Cashbox Lines", ondelete='cascade')

    _sql_constraints = [('uniq_name', 'unique(name)', "The name of this Cash Session must be unique !")]

    # @api.multi
    def _compute_picking_count(self):
        for pos in self:
            pickings = pos.order_ids.mapped('picking_id').filtered(lambda x: x.state != 'done')
            pos.picking_count = len(pickings.ids)

    # @api.multi
    # def action_stock_picking(self):
    #    pickings = self.order_ids.mapped('picking_id').filtered(lambda x: x.state != 'done')
    #    action_picking = self.env.ref('stock.action_picking_tree_ready')
    #    action = action_picking.read()[0]
    #    action['context'] = {}
    #    action['domain'] = [('id', 'in', pickings.ids)]
    #    return action

    @api.depends('config_id', 'statement_ids')
    def _compute_cash_all(self):
        balance_start = 0.00
        saldo_inicial = 0.00
        balance_end = 0.00
        balance_end_real = 0.00
        total_entry_encoding = 0.00
        difference = 0.00
        for session in self:
            saldo_inicial = session.cash_register_balance_start
            session.cash_journal_id = session.cash_register_id = session.cash_control = False
            if session.config_id.cash_control:
                for statement in session.statement_ids:
                    if statement.journal_id.type == 'cash':
                        session.cash_control = True
                        session.cash_journal_id = statement.journal_id.id
                        session.cash_register_id = statement.id
                        balance_start += statement.balance_start
                        balance_end += statement.balance_end
                        balance_end_real += statement.balance_end_real
                        total_entry_encoding += statement.total_entry_encoding
                        difference += statement.difference
                # if not session.cash_control and session.state != 'closed':
                # raise UserError(_("Cash control can only be applied to cash journals."))
            session.cash_register_balance_start = saldo_inicial + balance_start
            session.cash_register_balance_end = balance_end
            session.cash_register_balance_end_real = balance_end_real
            session.cash_register_total_entry_encoding = total_entry_encoding
            session.cash_register_difference = difference

    @api.constrains('user_id', 'state')
    def _check_unicity(self):
        # open if there is no session in 'opening_control', 'opened', 'closing_control' for one user
        if self.search_count([
            ('state', 'not in', ('closed', 'closing_control')),
            ('user_id', '=', self.user_id.id),
            ('rescue', '=', False)
        ]) > 1:
            raise ValidationError(
                _("You cannot create two active sessions with the same responsible."))

    @api.constrains('config_id')
    def _check_pos_config(self):
        if self.search_count([
            ('state', '!=', 'closed'),
            ('config_id', '=', self.config_id.id),
            ('rescue', '=', False)
        ]) > 1:
            raise ValidationError(_("Another session is already opened for this cash session."))

    @api.model
    def create(self, values):
        config_id = values.get('config_id') or self.env.context.get('default_config_id')
        config_id = self.env['cash.config'].search([('user_id', '=', self.env.uid)], limit=1).id
        if not config_id:
            raise UserError(_("You should assign a Cash to your session."))

        # journal_id is not required on the pos_config because it does not
        # exists at the installation. If nothing is configured at the
        # installation we do the minimal configuration. Impossible to do in
        # the .xml files as the CoA is not yet installed.
        pos_config = self.env['cash.config'].browse(config_id)
        ctx = dict(self.env.context, company_id=pos_config.company_id.id)
        if not pos_config.journal_id:
            default_journals = pos_config.with_context(
                ctx).default_get(['journal_id', 'invoice_journal_id'])
            if (not default_journals.get('journal_id') or
                    not default_journals.get('invoice_journal_id')):
                raise UserError(
                    _("Unable to open the session. You have to assign a sales journal to your cash config."))
            pos_config.with_context(ctx).sudo().write({
                'journal_id': default_journals['journal_id'],
                'invoice_journal_id': default_journals['invoice_journal_id']})
        # define some cash journal if no payment method exists
        if not pos_config.journal_ids:
            Journal = self.env['account.journal']
            journals = Journal.with_context(ctx).search(
                [('journal_user', '=', True), ('type', '=', 'cash')])
            if not journals:
                journals = Journal.with_context(ctx).search([('type', '=', 'cash')])
                if not journals:
                    journals = Journal.with_context(ctx).search([('journal_user', '=', True)])
            journals.sudo().write({'journal_user': True})
            pos_config.sudo().write({'journal_ids': [(6, 0, journals.ids)]})

        pos_name = self.env['ir.sequence'].with_context(ctx).next_by_code('cash.session')
        if values.get('name'):
            pos_name += ' ' + values['name']

        statements = []
        ABS = self.env['account.bank.statement']
        uid = SUPERUSER_ID
        for journal in pos_config.journal_ids:
            # set the journal_id which should be used by
            # account.bank.statement to set the opening balance of the
            # newly created bank statement
            ctx['journal_id'] = journal.id if pos_config.cash_control and journal.type == 'cash' else False
            st_values = {
                'journal_id': journal.id,
                'user_id': self.env.user.id,
                'balance_start': self._get_opening_balance(journal.id),
                'name': pos_name
            }

            statements.append(ABS.with_context(ctx).sudo(uid).create(st_values).id)

        values.update({
            'name': pos_name,
            'statement_ids': [(6, 0, statements)],
            'config_id': config_id
        })

        res = super(CashSession, self.with_context(ctx).sudo(uid)).create(values)
        if not pos_config.cash_control:
            res.action_cash_session_open()

        return res

    #@api.multi
    def unlink(self):
        for session in self.filtered(lambda s: s.statement_ids):
            session.statement_ids.unlink()
        return super(CashSession, self).unlink()

    #@api.multi
    def login(self):
        self.ensure_one()
        self.write({
            'login_number': self.login_number + 1,
        })

    #@api.multi
    def action_cash_session_open(self):
        # second browse because we need to refetch the data from the DB for cash_register_id
        # we only open sessions that haven't already been opened
        for session in self.filtered(lambda session: session.state == 'opening_control'):
            values = {}
            if not session.start_at:
                values['start_at'] = fields.Datetime.now()
            values['state'] = 'opened'
            session.write(values)
            #session.statement_ids.button_open()
        return True

    #@api.multi
    def action_cash_session_closing_control(self):
        self._check_cash_session_balance()
        for session in self:
            session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            if not session.config_id.cash_control:
                session.action_cash_session_close()

    #@api.multi
    def _check_cash_session_balance(self):
        for session in self:
            for statement in session.statement_ids:
                if (statement != session.cash_register_id) and (statement.balance_end != statement.balance_end_real):
                    statement.write({'balance_end_real': statement.balance_end})

    #@api.multi
    def action_cash_session_validate(self):
        self._check_cash_session_balance()
        self.action_cash_session_close()

    #@api.multi
    def action_cash_session_close(self):
        # Close CashBox
        for session in self:
            company_id = session.config_id.company_id.id
            ctx = dict(self.env.context, force_company=company_id, company_id=company_id)
            for st in session.statement_ids:
                if abs(st.difference) > st.journal_id.amount_authorized_diff:
                    # The pos manager can close statements with maximums.
                    if not self.user_has_groups("account.group_account_manager"):
                        raise UserError(_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (
                            st.difference, st.journal_id.amount_authorized_diff))
                if (st.journal_id.type not in ['bank', 'cash']):
                    raise UserError(
                        _("The journal type for your payment method should be bank or cash."))
                #if st.amount < 0.00:
                st.with_context(ctx).sudo().button_post()
        #self.with_context(ctx)._confirm_orders()
        #self._reconcile_payments_invoices(session.order_ids)
        self.write({'state': 'closed'})
        return {
            'type': 'ir.actions.client',
            'name': 'Sessions',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('cash_session.menu_cash_session_all').id},
        }

    #@api.multi
    def open_cashbox(self):
        self.ensure_one()
        session_id = self.env.context.get('active_id', False)
        context = dict(self._context)
        balance_type = context.get('balance') or 'start'
        context['bank_statement_id'] = self.cash_register_id.id
        context['balance'] = balance_type
        context['default_cash_session_id'] = self.id
        context['default_cash_id'] = self.config_id.id

        action = {
            'name': _('Cash Control'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement.cashbox',
            'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

        cashbox_id = None
        if balance_type == 'start':
            cashbox_id = self.cash_register_id.cashbox_start_id.id
        else:
            cashbox_id = self.cash_register_id.cashbox_end_id.id
        if cashbox_id:
            action['res_id'] = cashbox_id

        return action

    #@api.multi
    def _get_opening_balance(self, journal_id):
        abs_obj = self.env['account.bank.statement']
        if journal_id:
            last_bnk_stmt = abs_obj.search([('journal_id', '=', journal_id)], limit=1)
            if last_bnk_stmt:
                return last_bnk_stmt.balance_end
        return 0