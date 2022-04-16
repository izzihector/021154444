from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    local_currency_price = fields.Float()
    rate_exchange = fields.Float(related='move_id.rate_exchange')
    currency_id = fields.Many2one(
        'res.currency', related='move_id.currency_id')

    @api.onchange('rate_exchange', 'price_unit', 'quantity')
    def account_invoice_line(self):

        if self.move_id.check_rate and self.move_id.rate_exchange:
            self.local_currency_price = self.quantity * \
                self.price_unit*self.move_id.rate_exchange
