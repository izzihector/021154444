# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    check_rate = fields.Boolean()
    rate_exchange = fields.Float()
    currency = fields.Many2one('res.currency', string="Currency")

    @api.onchange('rate_exchange')
    def update_cost_lines(self):

        for data in self.cost_lines:
            data.price_unit = data.currency_value*self.rate_exchange
