# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models
from datetime import datetime
from num2words import num2words
from .money_to_text_ar import amount_to_text_arabic



class AccountMoveInherit(models.Model):
    _inherit = 'account.move'


    def compute_amount_in_word(self,amount):
        if self.env.user.lang == 'en_US':
            num_word = str(self.currency_id.amount_to_text(amount)) + ' only'
            return num_word
        elif self.env.user.lang == 'ar_001':
            num_word = num2words(amount, to='currency', lang=self.env.user.lang)
            num_word = str(num_word) + ' فقط'
            return num_word
    def amount_text_arabic(self,amount):
        return amount_to_text_arabic(amount, self.company_id.currency_id.name)