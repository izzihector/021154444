# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class reportes_xetechs(models.Model):
#     _name = 'reportes_xetechs.reportes_xetechs'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    MAX_LINES = None
