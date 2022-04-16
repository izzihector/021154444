from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.depends("price_unit")
    def _compute_unit_mrp_price(self):
        for stock in self:
            purchase_order = self.env['purchase.order'].search([('name', '=', stock.origin)])
            purchase_order_line = self.env['purchase.order.line'].search(
                [('product_id', '=', stock.product_id.id), ('order_id', '=', purchase_order.id)])
            print("purchase_order_line.price_unit:", purchase_order_line.price_unit)
            stock.price_unit = purchase_order_line.price_unit

    list_price = fields.Float("Sales Price", related="product_id.list_price", stored=True, readonly=False)
    mrp_unit = fields.Float("MRP", stored=True, related="product_id.mrp_unit", readonly=False)
    price_unit = fields.Float("Purchase Rate", compute=_compute_unit_mrp_price, stored=True)
    price_cogs = fields.Float("COGS", related="product_id.standard_price", stored=True)
    lot_name = fields.Char('Lot/Serial Number Name', readonly=True)


    @api.onchange('mrp_unit')
    def _lot_based_on_unit_mrp_price(self):
        stock_production_lot = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('cost_price', '=', self.price_unit), ('mrp_unit', '=', self.mrp_unit)])
        print("stock_production_lot:", stock_production_lot)
        if stock_production_lot:
            self.lot_id = stock_production_lot[0].id
        else:
            self.lot_id = False

    @api.onchange('mrp_unit')
    def _mrp_validation(self):
        try:
            mrp = self.mrp_unit
            purchase_rate = self.price_unit
            if purchase_rate > mrp:
                _logger.info('### purchase rate is gather than mrp')
                raise UserError(_("Purchase Rate must be gather than MRP"))
            elif purchase_rate == mrp:
                stock_production_lot = self.env['stock.production.lot'].search(
                    [('product_id', '=', self._origin.product_id.id)], order='id desc')
                self.update({
                    'list_price': stock_production_lot[0].list_price
                })
            else:
                self.update({
                    'list_price': 0
                })

        except ValueError as e:
            print("e:", e)
            raise UserError(_('MRP set failed, please check MRP value'))




