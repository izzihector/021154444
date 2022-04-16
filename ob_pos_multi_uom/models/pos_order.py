# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosOrderExtended(models.Model):
    _inherit = 'pos.order'

    def _prepare_invoice_line(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.qty if self.amount_total >= 0 else -order_line.qty,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit,
            'name': order_line.product_id.display_name,
            'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id': order_line.uom_id.id,
        }


class PosOrderLinesExtended(models.Model):
    _inherit = 'pos.order.line'

    uom_id = fields.Many2one('uom.uom', string="UOM")

    @api.model
    def create(self, values):

        if values.get('uom_id'):
            values['uom_id'] = values['uom_id']['id']
        else:
            values['uom_id'] = None
        res = super(PosOrderLinesExtended, self).create(values)
        return res
