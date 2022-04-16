from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one('res.partner', string='Customer',
                                 domain="['|', '&', ('customer_rank', '=', False), ('customer_rank', '>', 0), ('partner_type', '=', 'b2b')]")