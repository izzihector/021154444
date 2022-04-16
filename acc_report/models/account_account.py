# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = "account.account"

    ma = fields.Float(string="MA", digits=dp.get_precision('MA'))
    ragio = fields.Float(string="Ragio", digits=dp.get_precision('Ragio'))
    cargo = fields.Float(string="Cargo", digits=dp.get_precision('Cargo'))
    total_group_id = fields.Many2one('total.group', string="Total Group")
    group_type = fields.Selection([
                                  ('income', 'Income'),
                                  ('expense', 'Expense'),
                                  ('other_income', 'Other Income'),
                                  ('other_expense', 'Other Expense'),
                                  ], string="Group Type")

    
    def write(self, vals):
        res = super(AccountAccount, self).write(vals)
        total = self.ma + self.ragio + self.cargo
        if total == 0.0:
            return res
        if total != 100:
            raise UserError(_("Total(MA+Ragio+Cargo) Must be 100%"))
        return res

    @api.model
    def create(self, vals):
        res = super(AccountAccount, self).create(vals)
        if res:
            total = res.ma + res.ragio + res.cargo
            if total == 0.0:
                return res
            if total > 0 and total != 100:
                raise UserError(_("Total(MA+Ragio+Cargo) Must be 100%"))
        return res


class TotalGroup(models.Model):
    _name = 'total.group'

    name = fields.Char('Group', required=True, copy=False)
