# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api, _
from datetime import date, time, datetime


class PartnerCreditHistory(models.Model):
    _inherit = 'res.partner'
    _description = "partner"
    
    credit_ids = fields.One2many('credit.history', 'partner_id', string='Credit History')
    update_credit_ids = fields.One2many('update.credit.history', 'partner_id', string='Update Credit History')
    update_credit_payment_ids = fields.One2many('update.credit.history.payment', 'partner_id', string='Update Credit History with Accounting Entry')

    def create_credit_history(self, used_credit_amount, balance_credit_amount, partner_id, order):
        
        credit_history_obj = self.env['credit.history']
        credit_history_obj.create({
            'used_credit_amount' : used_credit_amount,
            'balance_credit_amount': balance_credit_amount,
            'partner_id': partner_id['id'],
        })


class CreditHistory(models.Model):
    _name = 'credit.history'
    _description = "Credit History"
    
    date = fields.Date('Date')
    pos_order_id = fields.Many2one('pos.order', 'POS Order')
    pos_order_amount = fields.Float('POS Order Amount')
    used_credit_amount = fields.Float('Used Credit Amount')
    balance_credit_amount = fields.Float('Balance Credit Amount')
    partner_id = fields.Many2one('res.partner', 'Customer')
    bill_id = fields.Integer('Bill ID')
    
    
        
