# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)


class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    currency_value = fields.Float()

    @api.onchange('currency_value')
    def stock_landed_cost_lines(self):

        if self.cost_id.check_rate:
            self.price_unit = self.currency_value * self.cost_id.rate_exchange

        else:
            self.price_unit = self.currency_value
