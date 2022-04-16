from odoo import models, fields, api
from .money_to_text_ar import amount_to_text_arabic

class PaymentInherit(models.Model):
    _inherit = 'account.payment'

    def amount_text_arabic(self, amount):
        return amount_to_text_arabic(amount, self.company_id.currency_id.name)

