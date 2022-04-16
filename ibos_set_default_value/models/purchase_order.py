from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_id = fields.Many2one('res.partner', string='Supplier', domain="['|', ('supplier_rank', '=', False), ('supplier_rank', '>', 0)]")