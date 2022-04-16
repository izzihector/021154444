from odoo import fields, models, api

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    api_origin = fields.Char('API Origin')