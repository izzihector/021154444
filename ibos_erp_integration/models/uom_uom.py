from odoo import fields, models, api

class UomUom(models.Model):
    _inherit = 'uom.uom'

    api_origin = fields.Char('API Origin')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)