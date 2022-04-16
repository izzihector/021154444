# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api, _
from datetime import date, time, datetime
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)
import psycopg2


class res_partner(models.Model):
    _inherit = 'res.partner'

    custom_credit = fields.Float('Credit')
    credit_limit = fields.Float('Credit Limit')

    def action_view_credit_detail(self):
        self.ensure_one()

        partner_credit_ids = self.env['partner.credit'].search([('partner_id', '=', self.id)])
        for payment_id in partner_credit_ids:
            self.env['partner.credit'].browse(payment_id)
            payment_id.do_update()

        return {
            'name': 'Credit Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'partner.credit',
            'domain': [('partner_id', '=', self.id)],
        }

    def UpdateCredit(self, partner_id, company_id, pos_currency_id, custom_credit):
        pos_curr = self.env['res.currency'].browse(pos_currency_id)
        company_details = self.env['res.company'].browse(company_id[0])
        partner_details = self.env['res.partner'].browse(partner_id['id'])
        res = False
        if (pos_curr.id != company_details.currency_id.id):
            currency_rate = pos_curr.rate / company_details.currency_id.rate
            new_credit = custom_credit / currency_rate
            credit_update = partner_details.custom_credit - new_credit
            res = partner_details.write({'custom_credit': credit_update})
            return res
        else:
            credit_update = partner_details.custom_credit - custom_credit
            res = partner_details.write({'custom_credit': credit_update})
            return res

    def CheckCredit(self, partner_id, company_id, pos_currency_id, custom_credit):
        pos_curr = self.env['res.currency'].browse(pos_currency_id)
        company_details = self.env['res.company'].browse(company_id[0])
        partner_details = self.env['res.partner'].browse(partner_id['id'])
        res = False

        if (pos_curr.id != company_details.currency_id.id):
            currency_rate = pos_curr.rate / company_details.currency_id.rate
            new_credit = custom_credit / currency_rate
            return new_credit
        else:
            return custom_credit


class partner_credit(models.Model):
    _name = 'partner.credit'
    _description = "partner Credit"

    partner_id = fields.Many2one('res.partner', "Customer")
    credit_jr = fields.Float('Credit', readonly=True)
    update = fields.Float('Update')

    @api.model
    def create(self, vals):
        return super(partner_credit, self).create(vals)

    def do_update(self):
        # update_value_get = self.env.context.get['update']
        update_credit_history_obj = self.env['update.credit.history']

        # print('update_value_get', update_value_get)
        if self.update > 0.00:
            self.credit_jr = self.update
            val = {
                'date_update': datetime.now(),
                'update_credit_amount': self.update,
                'old_credit_bal': self.partner_id.custom_credit,
                'balance': self.partner_id.custom_credit + self.update,
                'partner_id': self.partner_id.id,
            }
            update_credit_history_obj.create(val)
            # print('before credit update, partner credit consumed amount is', self.partner_id.custom_credit)
            self.partner_id.custom_credit = self.partner_id.custom_credit + self.credit_jr
            # print('after credit update, partner credit consumed amount is', self.partner_id.custom_credit)

            # print('before credit_limit update, partner credit_limit amount is', self.partner_id.credit_limit)
            # self.partner_id.credit_limit = self.partner_id.credit_limit + -(self.credit_jr)
            # print('after credit_limit update, partner credit_limit amount is', self.partner_id.credit_limit)
            self.credit_jr = self.partner_id.custom_credit
        elif self.env.context.get('update') > 0.00:
            # print('update value get',self.env.context.get('update'))
            self.credit_jr = self.env.context.get('update')
            val = {
                'date_update': datetime.now(),
                'update_credit_amount': self.env.context.get('update'),
                'old_credit_bal': self.partner_id.custom_credit,
                'balance': self.partner_id.custom_credit + self.env.context.get('update'),
                'partner_id': self.partner_id.id,
            }
            update_credit_history_obj.create(val)
            self.partner_id.custom_credit = self.partner_id.custom_credit + self.credit_jr
            self.credit_jr = self.partner_id.custom_credit

        if self.partner_id.custom_credit != 0.00:
            self.credit_jr = self.partner_id.custom_credit
        self.update = 0.00

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            update = self.partner_id.update
            return {'credit_jr': update}


class UpdateCreditHistory(models.Model):
    _name = 'update.credit.history'
    _description = "Update Credit History"

    date_update = fields.Date('Date')
    update_credit_amount = fields.Float('Update Credit amount')
    old_credit_bal = fields.Float('Old Credit Balance')
    balance = fields.Float('Balance')
    partner_id = fields.Many2one('res.partner', 'Customer')
    is_payment_received = fields.Boolean("Is Payment Received", default=False)
    api_origin = fields.Char('API Origin')


class UpdateCreditHistoryPayment(models.Model):
    _name = 'update.credit.history.payment'
    _description = "Update Credit History Payment"

    date_update = fields.Date('Date')
    update_credit_amount = fields.Float('Update Credit amount')
    old_credit_bal = fields.Float('Old Credit Balance')
    payment_refer = fields.Many2one('account.payment', 'Payment Ref.')
    balance = fields.Float('Balance')
    partner_id = fields.Many2one('res.partner', 'Customer')


class UpdateCreditAccount(models.TransientModel):
    _name = 'credit.account'
    _description = "Credit Account"

    credit_amount = fields.Float('Credit Amount', required="True")
    journal_id = fields.Many2one('account.journal', 'Payment Journal',
                                 required=True, domain=[('type', 'in', ['cash', 'bank']), ('credit_jr', '=', False)])
    credit_id = fields.Many2one('partner.credit', 'Customer')

    # partner_id = fields.Many2one('res.partner', 'Customer', related='credit_id.partner_id')

    def post(self):
        context = self._context
        active_ids = context.get('active_ids')
        account_payment_obj = self.env['account.payment']
        partner_credit_id = self.env['partner.credit'].browse(active_ids[0])
        update_credit_payment_history_obj = self.env['update.credit.history.payment']

        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d')

        vals = {}

        vals = {
            'name': self.env['ir.sequence'].with_context(ir_sequence_date=date_now).next_by_code(
                'account.payment.customer.invoice'),
            'payment_type': "inbound",
            'amount': self.credit_amount,
            'date': datetime.now().date(),
            'journal_id': self.journal_id.id,
            'payment_method_id': 1,
            'partner_type': 'customer',
            'partner_id': partner_credit_id.partner_id.id,
        }

        payment_create = account_payment_obj.create(vals)
        payment_create.action_post()
        if partner_credit_id.credit_jr >= 0.00:
            partner_credit_id.credit_jr = payment_create.amount
            value = {
                'date_update': datetime.now(),
                'update_credit_amount': partner_credit_id.credit_jr,
                'old_credit_bal': partner_credit_id.partner_id.custom_credit,
                'balance': partner_credit_id.partner_id.custom_credit + partner_credit_id.credit_jr,
                'partner_id': partner_credit_id.partner_id.id,
                'payment_refer': payment_create.id,
            }
            update_credit_payment_history_obj.create(value)
            partner_credit_id.partner_id.custom_credit = partner_credit_id.partner_id.custom_credit + partner_credit_id.credit_jr

        if partner_credit_id.partner_id.custom_credit != 0.00:
            partner_credit_id.credit_jr = partner_credit_id.partner_id.custom_credit

        return
