# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.addons import decimal_precision as dp
# from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    ma = fields.Float(string="MA", digits=dp.get_precision('MA'), readonly=True, track_visibility='onchange')
    ragio = fields.Float(string="Ragio", digits=dp.get_precision('Ragio'), readonly=True, track_visibility='onchange')
    cargo = fields.Float(string="Cargo", digits=dp.get_precision('Cargo'), readonly=True, track_visibility='onchange')
    cost_group_id = fields.Many2one('cost.group', string="Cost Group", readonly=True, track_visibility='onchange')
    process_flow_id = fields.Many2one('process.flow', string="Process Flow", readonly=True, track_visibility='onchange')

    # 
    # def write(self, vals):
    #     res = super(AccountAnalyticAccount, self).write(vals)
    #     total = self.ma + self.ragio + self.cargo
    #     if total == 0.0:
    #         return res
    #     if total != 100:
    #         raise UserError(_("Total(MA+Ragio+Cargo) Must be 100%"))
    #     return res

    # @api.model
    # def create(self, vals):
    #     res = super(AccountAnalyticAccount, self).create(vals)
    #     if res:
    #         total = res.ma + res.ragio + res.cargo
    #         if total == 0.0:
    #             return res
    #         if total > 0 and total != 100:
    #             raise UserError(_("Total(MA+Ragio+Cargo) Must be 100%"))
    #     return res
