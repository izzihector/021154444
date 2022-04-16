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



class AccountPaymentsInherit(models.Model):
    _inherit = 'account.payment'


    def _compute_amount_in_word(self):
        for rec in self:
            if self.env.user.lang == 'en_US':
                rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
            elif self.env.user.lang == 'ar_001':
                rec.num_word = num2words(rec.amount_total, to='currency', lang=self.env.user.lang)
                rec.num_word = str(rec.num_word) + ' فقط'

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')

# class SaleOrder(models.Model):
#
#     _inherit = 'sale.order'
#
#
#     # @api.multi
#     def _compute_amount_in_word(self):
#         for rec in self:
#             # lang = self.company_id.text_amount_language_currency
#             # rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#
#             rec.num_word_ar = num2words(self.amount_total, to='currency',
#                                          lang='ar')
#
#             if 'ثلاثة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ثلاثة مئة", "ثلاثمائة")
#                 rec.num_word_ar = x
#             if 'أربعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("أربعة مئة", "أربعمائة")
#                 rec.num_word_ar = x
#             if 'خمسة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("خمسة مئة", "خمسمائة")
#                 rec.num_word_ar = x
#             if 'ستة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ستة مئة", "ستمائة")
#                 rec.num_word_ar = x
#             if 'سبعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("سبعة مئة", "سبعمائة")
#                 rec.num_word_ar = x
#             if 'ثمانية مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ثمانية مئة", "ثمانمائة")
#                 rec.num_word_ar = x
#             if 'تسعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("تسعة مئة", "تسعمائة")
#                 rec.num_word_ar = x
#
#             if self.env.user.lang == 'en_US':
#                 rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#             elif self.env.user.lang == 'ar_001':
#                 rec.num_word = num2words(rec.amount_total, to='currency',
#                                          lang=self.env.user.lang)
#
#             rec.num_word_en = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#
#             # rec.num_word_en = num2words(rec.amount_total, to='currency',currency=rec.currency_id.name,
#             #                              lang='en')
#
#
#
#
#             print(self.env.user.lang)
#     num_word_ar = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
#     num_word_en = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
#     num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')

# class PurchaseOrder(models.Model):
#
#     _inherit = 'purchase.order'
#
#
#     # @api.multi
#     def _compute_amount_in_word(self):
#         for rec in self:
#             # lang = self.company_id.text_amount_language_currency
#             # rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#
#             rec.num_word_ar = num2words(self.amount_total, to='currency',
#                                          lang='ar')
#
#             if 'ثلاثة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ثلاثة مئة", "ثلاثمائة")
#                 rec.num_word_ar = x
#             if 'أربعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("أربعة مئة", "أربعمائة")
#                 rec.num_word_ar = x
#             if 'خمسة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("خمسة مئة", "خمسمائة")
#                 rec.num_word_ar = x
#             if 'ستة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ستة مئة", "ستمائة")
#                 rec.num_word_ar = x
#             if 'سبعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("سبعة مئة", "سبعمائة")
#                 rec.num_word_ar = x
#             if 'ثمانية مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ثمانية مئة", "ثمانمائة")
#                 rec.num_word_ar = x
#             if 'تسعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("تسعة مئة", "تسعمائة")
#                 rec.num_word_ar = x
#
#             if self.env.user.lang == 'en_US':
#                 rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#             elif self.env.user.lang == 'ar_001':
#                 rec.num_word = num2words(rec.amount_total, to='currency',
#                                          lang=self.env.user.lang)
#
#             rec.num_word_en = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#
#             # rec.num_word_en = num2words(rec.amount_total, to='currency',currency=rec.currency_id.name,
#             #                              lang='en')
#
#
#             print('current land')
#             print(self.env.user.lang)
#
#     num_word_ar = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
#     num_word_en = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
#     num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')

# class InvoiceOrder(models.Model):
#
#     _inherit = 'account.move'
#
#
#     # @api.multi
#     def _compute_amount_in_word(self):
#         for rec in self:
#             # lang = self.company_id.text_amount_language_currency
#             # rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#
#             rec.num_word_ar = num2words(self.amount_total, to='currency',
#                                          lang='ar')
#
#             if 'ثلاثة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ثلاثة مئة", "ثلاثمائة")
#                 rec.num_word_ar = x
#             if 'أربعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("أربعة مئة", "أربعمائة")
#                 rec.num_word_ar = x
#             if 'خمسة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("خمسة مئة", "خمسمائة")
#                 rec.num_word_ar = x
#             if 'ستة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ستة مئة", "ستمائة")
#                 rec.num_word_ar = x
#             if 'سبعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("سبعة مئة", "سبعمائة")
#                 rec.num_word_ar = x
#             if 'ثمانية مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("ثمانية مئة", "ثمانمائة")
#                 rec.num_word_ar = x
#             if 'تسعة مئة' in rec.num_word_ar:
#                 x = rec.num_word_ar.replace("تسعة مئة", "تسعمائة")
#                 rec.num_word_ar = x
#
#             if self.env.user.lang == 'en_US':
#                 rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#             elif self.env.user.lang == 'ar_001':
#                 rec.num_word = num2words(rec.amount_total, to='currency',
#                                          lang=self.env.user.lang)
#
#             rec.num_word_en = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
#
#             # rec.num_word_en = num2words(rec.amount_total, to='currency',currency=rec.currency_id.name,
#             #                              lang='en')
#
#
#
#
#             print(self.env.user.lang)
#     num_word_ar = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
#     num_word_en = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
#     num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
