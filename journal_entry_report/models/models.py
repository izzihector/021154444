from odoo import models, fields, api
from num2words import num2words
from .money_to_text_ar import amount_to_text_arabic

class JournalItem(models.Model):
    _inherit = 'account.move.line'
    sequence_number = fields.Integer('Number')

class JournalEntry(models.Model):
    _inherit = 'account.move'

    posted_user = fields.Many2one('res.users')

    def _post(self, soft=True):
        self.posted_user = self.env.user.id
        return super()._post(soft)


    def compute_amount_in_word_ar(self, amount):
        # num_word = num2words(amount, to='currency', lang='ar')
        # num_word = str(num_word) + ' فقط'
        # num_str = num_word.replace('trillion','تريليون').replace('billion','مليار')
        # num_word = str(self.currency_id.with_context(lang='ar_001').amount_to_text(amount)) + ' only'
        num_str = amount_to_text_arabic(amount, self.company_id.currency_id.name)
        return num_str

    def compute_amount_in_word_en(self, amount):
        num_word = str(self.currency_id.amount_to_text(amount)) + ' only'
        return num_word
