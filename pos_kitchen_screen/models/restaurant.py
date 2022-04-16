# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models,_
import datetime
from functools import partial
import logging
_logger = logging.getLogger(__name__)


class PosKitchenOrder(models.Model):
	_name = 'pos.kitchen.order'
	_order = 'id desc'
	_rec_name = 'pos_reference'

	name = fields.Char(string="Name")
	is_changed = fields.Boolean(default=False,string="Is Changed")
	order_progress = fields.Selection([('cancel',"Cancel"),('pending','Pending'),('done','Done'),('partially_done','Partially Done'),('new','New')],string="Order Progress")
	config_id = fields.Many2one('pos.config',string="POS Config")
	session_id = fields.Many2one('pos.session',string="POS Session")
	is_state_updated = fields.Boolean(string="Is state Updated")
	kitchen_order_name = fields.Char(string="Token NO.")
	user_id = fields.Many2one('res.users',string="Users")
	amount_total = fields.Float(string="Amount Total")
	out_of_stock_products = fields.One2many('product.product','related_kitchen_order',string="Out Of Stock Products")
	cancellation_reason = fields.Char(string="Cancellation Reason")
	pos_reference = fields.Char(string="Pos Reference")
	partner_id = fields.Many2one('res.partner',string="Partner")
	date_order = fields.Datetime(string="DateTime")
	lines = fields.One2many('pos.kitchen.orderline','order_id',string="kitchen Orderlines")
	order_type = fields.Selection([('pos','Point Of Sale'),('kitchen','Kitchen')],string="Order Type")
	is_kitchen_order = fields.Boolean(string="Is Kitchen Order")


class PosKitchenOrderLines(models.Model):
	_name = 'pos.kitchen.orderline'

	order_id = fields.Many2one('pos.kitchen.order',string="Related Pos Order")
	display_name = fields.Char(string="Display Name")
	is_orderline_done = fields.Boolean(string="Is Orderline Done",default=False)
	product_id = fields.Many2one('product.product',string="Product")
	state = fields.Selection([('cancel',"Cancel"),('in_process','In Process'),('done','Done'),('in_queue','In Queue'),('new','New')],string="State",default="new")
	qty = fields.Integer(string="Quantity")
	note = fields.Char(string="Note")
	previous_quantity = fields.Integer(string="Previous Quantity")
	previous_first_quantity = fields.Integer(string="Previous First Quantity")
	qty_added = fields.Integer(string="Quantities Added")
	qty_removed = fields.Integer(string="Quantities Removed")
	total_qtys = fields.Integer(string="Total Quantities")
	price_unit = fields.Float(string="Price")
	full_product_name = fields.Char(string="Full Product Name")


class PosKitchenConfig(models.Model):
	_inherit = 'pos.kitchen.screen.config'

	is_changed = fields.Boolean(default=False,string="Is Changed")
