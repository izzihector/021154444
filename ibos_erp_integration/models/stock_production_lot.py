from odoo import fields, models, api

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", store=True)
    last_sales_price = fields.Float('Last Sales Price', store=True)
    mrp_unit = fields.Float('MRP',  store=True)
    cost_price = fields.Float("Cost Price", store=True)
    price_unit = fields.Float("Purchase Rate", store=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id',  store=True)
    discount = fields.Float("Discount",  store=True)
    discount_percent = fields.Float("Discount(%)",  store=True)


    @api.onchange("list_price")
    def set_discount_with_percentange(self):
        discount = self.mrp_unit - self.list_price
        discount_percent = (discount * self.mrp_unit) / 100
        self.update({
            'discount': discount,
            'discount_percent': discount_percent
        })

    def write(self, vals):
        discount = self.mrp_unit - self.list_price
        discount_percent = (discount * self.mrp_unit)/100
        vals.update({
            'discount': discount,
            'discount_percent': discount_percent
        })
        return super(StockProductionLot, self).write(vals)
