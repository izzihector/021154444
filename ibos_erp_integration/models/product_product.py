from odoo import fields, models, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    api_origin = fields.Char('API Origin', stored=True)
    image_id = fields.Char('ERP Image')
    mrp_unit = fields.Float("MRP")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    product_bangla_name = fields.Char('Bangla Name', readonly=False)
