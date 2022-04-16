# -*- encoding: UTF-8 -*-

from odoo import api, fields, models, _
from .mandatory_analytic_account import MandatoryAnalyticAccount


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    required_flight_number = fields.Boolean('Is the fligh number required? (internal field)',
                                            compute='_is_flight_number_required')

    @api.multi
    @api.onchange('account_id')
    def _filter_analytic_account(self):
        for record in self:
            if record.account_id:
                code = record.account_id.code
                if (code[0] in ['4', '8', '9']) and code != '999999':
                    record.required_analytic_account = True
                else:
                    record.required_analytic_account = False
                analytic_accounts = MandatoryAnalyticAccount.search_mandatory_accounts(code, self.env.cr)
                record.account_analytic_id = None
                if analytic_accounts:
                    res = {
                        'domain': {'account_analytic_id': [('id', 'in', analytic_accounts)]}
                    }
                else:
                    res = {
                        'domain': {'account_analytic_id': []}
                    }
                return res

    @api.depends('analytic_account_id', 'account_id')
    def _is_flight_number_required(self):
        for record in self:
            if record.account_id and record.analytic_account_id:
                if MandatoryAnalyticAccount.check_required_fligh_number(record.account_id.code,
                                                                        record.analytic_account_id.id,
                                                                        self.env.cr):
                    record.required_flight_number = True
