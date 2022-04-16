# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import float_is_zero, pycompat
from odoo.tools import float_compare, float_round, float_repr
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError, ValidationError

import time
import math

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    cash_session_id = fields.Many2one('cash.session', string="Session", copy=False)
    account_id = fields.Many2one('account.account', related='journal_id.default_account_id', readonly=True)

    #@api.multi
    #def button_confirm_bank(self):
    #    self._balance_check()
    #    statements = self.filtered(lambda r: r.state == 'open')
    #    for statement in statements:
    #        moves = self.env['account.move']
    #        for st_line in statement.line_ids:
    #            #upon bank statement confirmation, look if some lines have the account_id set. It would trigger a journal entry
    #            #creation towards that account, with the wanted side-effect to skip that line in the bank reconciliation widget.
    #            #if st_line.amount < 0
    #            if st_line.is_internal == False:
    #                st_line.fast_counterpart_creation()
    #                if not st_line.account_id and not st_line.journal_entry_ids.ids and not st_line.statement_id.currency_id.is_zero(st_line.amount):
    #                    raise UserError(_('All the account entries lines must be processed in order to close the statement.'))
    #                for aml in st_line.journal_entry_ids:
    #                    moves |= aml.move_id
    #                if moves:
    #                    moves.filtered(lambda m: m.state != 'posted').post()
    #        statement.message_post(body=_('Statement %s confirmed, journal items were created.') % (statement.name,))
    #    statements.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    # cash_statement_id = fields.Many2one('account.payment', string="Cash statement", ondelete='cascade')
    cash_statement_id = fields.Many2one('account.payment', string="Cash statement")
    is_internal = fields.Boolean('Internal', required=False, default=False)
    is_reconcile = fields.Boolean('Reconcile', required=False, default=False)
