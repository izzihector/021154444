from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging



_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    check_rate = fields.Boolean(help='Amount of units of the base currency with respect to the foreign currency')
    rate_exchange= fields.Float(help='Amount of units of the base currency with respect to the foreign currency')
    local_currency_price = fields.Monetary(readonly=1)

    @api.onchange('amount', 'rate_exchange')
    def currency_price(self):
        self.local_currency_price = self.rate_exchange* self.amount

