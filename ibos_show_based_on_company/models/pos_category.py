from odoo import fields, models, api

class PosCategory(models.Model):
    _inherit = 'pos.category'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)