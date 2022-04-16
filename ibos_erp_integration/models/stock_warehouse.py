from odoo import fields, models, api

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    api_origin = fields.Char('API Origin')
    sales_vat_required = fields.Boolean('Sales VAT Required')
    code = fields.Char('Short Name', required=True, size=15, help="Short name used to identify your warehouse")
    warehouse_address = fields.Char('Warehouse Address')
    company_id = fields.Many2one('res.company')