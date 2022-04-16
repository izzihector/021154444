# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)


class AccountMoveC(models.Model):

    _inherit = 'account.move'

    check_rate = fields.Boolean(
        help='Amount of units of the base currency with respect to the foreign currency')
    rate_exchange = fields.Float(
        help='Amount of units of the base currency with respect to the foreign currency')

    @api.onchange('check_rate')
    def line_ids_invoice(self):
        if not self.check_rate:
            for data in self.invoice_line_ids:
                data.local_currency_price = None
        else:
            for data in self.invoice_line_ids:
                data.local_currency_price = data.quantity*data.price_unit * self.rate_exchange

    @api.onchange('rate_exchange')
    def update_local_currency(self):
        for data in self.invoice_line_ids:
            data.local_currency_price = data.quantity*data.price_unit * self.rate_exchange
