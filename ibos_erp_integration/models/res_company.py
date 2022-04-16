from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    api_origin = fields.Char('API Origin')