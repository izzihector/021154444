from odoo import fields, models, api

class ResBranch(models.Model):
    _inherit = 'res.branch'

    api_origin = fields.Char('API Origin')