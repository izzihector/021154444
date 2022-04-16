from odoo import fields, models, api

class ResBank(models.Model):
    _inherit = 'res.bank'

    api_origin = fields.Char('API Origin')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)