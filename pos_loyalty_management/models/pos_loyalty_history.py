# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)

class PosLoyaltyHistory(models.Model):
    _name = "pos.loyalty.history"
    _description = "Manage the POS loyalty point history"
    _rec_name = "pos_order_id"
    _order = 'tx_date desc'

    pos_order_id = fields.Many2one('pos.order', string="Order Reference")
    session_id = fields.Many2one('pos.session', string="Session")
    customer_id = fields.Many2one('res.partner', string="Customer")
    tx_points = fields.Float(string="Transaction Points")
    remain_points = fields.Float(string="Current Points")
    salesman_id = fields.Many2one('res.users', string="Salesman")
    tx_type = fields.Selection([('credit', 'Credit'), ('debit', 'Debit')], string="Transaction Type")
    source = fields.Selection([('pos', 'Point of Sale'), ('website', 'Website')], string="Source", default='pos')
    tx_date = fields.Datetime(string="Transaction Time")

