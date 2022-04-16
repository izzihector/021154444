# -*- encoding: UTF-8 -*-

from odoo import api, fields, models, _


class ProfitCenter(models.Model):
    _name = "profit.center"

    name = fields.Char(string="Name")
    analytical_account_id = fields.Many2one('account.analytic.account', 'Analytical Account')