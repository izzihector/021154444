from odoo import fields, models, api

class ProductCategory(models.Model):
    _inherit = 'product.category'

    company_id = fields.Many2one('res.company')