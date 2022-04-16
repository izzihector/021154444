# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, Warning
from odoo.http import request
from functools import partial
import datetime
import logging
_logger = logging.getLogger(__name__)

class PosKitchenOrder(models.Model):
	_inherit = 'pos.kitchen.order'

	floor_id = fields.Many2one("restaurant.floor",string="Floor")
	table_id = fields.Many2one("restaurant.table",string="Table No")
	# @api.model
	# def cancel_kitchen_order(self,order_ref,pos_screen_id):
	# 	if order_ref:
	# 		order = self.search([('pos_reference','=',order_ref)])
	# 		if order:
	# 			order.write({
	# 				'order_progress':'cancel',
	# 				'is_changed':True
	# 			})
	# 	_logger.info("****pos creeddn 8id*****%r",pos_screen_id)
	# 	if pos_screen_id:
	# 		pos_screen_data = self.env['pos.kitchen.screen.config'].browse(pos_screen_id)
	# 		if pos_screen_data:
	# 			_logger.info("****pos_screen_data*****%r",pos_screen_data)
	# 			pos_screen_data.write({'is_changed':True})


	@api.model
	def cancel_kitchen_order(self,order_ref,pos_screen_id):
		if order_ref:
			order = self.search([('pos_reference','=',order_ref)])
			if order:
				order.write({
					'order_progress':'cancel',
					'is_changed':True,
					'cancellation_reason':'Order deleted From POS.'
				})
		if pos_screen_id and len(pos_screen_id):
			screen_ids = [int(i) for i in pos_screen_id]
			pos_screen_data = self.env['pos.kitchen.screen.config'].browse(screen_ids)
			if pos_screen_data:
				pos_screen_data.write({'is_changed':True})

	@api.model
	def update_kitchen_order_progress(self,data):
		order_progresses = []
		if len(data):
			int_list = [int(i) for i in data]
			orders = self.browse(int_list)
			order_progresses = orders.read(['order_progress'])
			_logger.info("*********Order_procgress******%r",order_progresses)
			orderlines = []
			for order in orders:
				orderlines += order.lines.ids
			orderline_qtys = self.env['pos.kitchen.orderline'].browse(orderlines).read(['total_qtys'])

		return {'progress':order_progresses,'qtys':orderline_qtys}

	@api.model
	def get_kitchen_order_data(self, data,changes):
		process_line = partial(self._kitchen_order_line_fields, session_id=data['pos_session_id'])
		config_id = self.env['pos.session'].browse(data['pos_session_id']).config_id
		res = {
			'user_id':      data['user_id'] or False,
			'config_id':   config_id.id,
			'session_id':   data['pos_session_id'],
			'lines':        [process_line(l) for l in data['lines']] if data['lines'] else False,
			'pos_reference': data['name'],
			'partner_id':   data['partner_id'] or False,
			'date_order':   data['creation_date'].replace('T', ' ')[:19],
			'amount_total':  data['amount_total'],
			'table_id':  data['table_id'],
			'floor_id':  data['floor_id'],

		}
		order = self.search([('pos_reference','=',data['name'])])
		_logger.info('get_kitchen_order_data--%r',(data))
		if data.get('is_kitchen_order') and not order:
			sequence_date_wise = self.env['token.perday'].search([],limit=1)
			#_logger.info('get_kitchen_order_data--%r',(sequence_date_wise.sequence_id._next()))
			if sequence_date_wise:
				res.update({'kitchen_order_name':sequence_date_wise.sequence_id._next(),
					'order_progress':'pending' if config_id.auto_accept else 'new'
				})
			else:
				self.env['token.perday'].search([]).unlink()
				sequence_date_wise = self.env['token.perday'].create({
					'name':"token"+datetime.date.today().strftime("%Y-%m-%d")
				})
				res.update({'kitchen_order_name':sequence_date_wise.sequence_id._next(),
					'order_progress':'pending' if config_id.auto_accept else 'new'
				})
		order_id = {}
		if not order:
			order = self.create(res)
			order_list = []
			order_line_list = []
			payment_list = []
			if(order):
				has_category_product = []
				config_id = order.config_id
				# if config_id.module_pos_restaurant:
				if hasattr(config_id,'order_action') and config_id.order_action == 'order_button':
					pos_screen_data = self.env['pos.kitchen.screen.config'].search([("pos_config_ids",'=ilike',config_id.id)])
					is_allowed_order = True
					if config_id.auto_accept:
						order.lines.write({'state':'in_process'})
					if len(pos_screen_data.pos_category_ids.ids):
						for line in order.lines:
							if not line.is_orderline_done:
								for cat in line.product_id.pos_categ_id:
									if cat.id in pos_screen_data.pos_category_ids.ids:
										has_category_product.append(line.product_id)
						if len(has_category_product) == 0:
							is_allowed_order = False
					if is_allowed_order:
						_logger.info('-------%r----',order.table_id)
						vals = {}
						vals['lines'] = []
						vals['name'] = order.name
						vals['amount_total'] = order.amount_total
						vals['pos_reference'] = order.pos_reference
						vals['table_id'] = [order.table_id and order.table_id.id or 1,order.table_id and order.table_id.name or '']
						vals['floor_id'] = [order.floor_id and order.floor_id.id or 1,order.floor_id and order.floor_id.name or '']
						vals['order_progress'] = order.order_progress
						vals['date_order'] = order.date_order
						vals['kitchen_order_name'] = order.kitchen_order_name
						if order.partner_id:
							vals['partner_id'] = [order.partner_id.id, order.partner_id.name]
						else:
							vals['partner_id'] = False
						vals['id'] = order.id
						for line in order.lines:
							if not line.is_orderline_done:
								count = 0
								for categ in line.product_id.pos_categ_id:
									if categ in pos_screen_data.pos_category_ids and not count:
										count += 1
										vals['lines'].append(line.id)
										line_vals = {}
										line_vals['display_name'] = line.display_name
										line_vals['id'] = line.id
										line_vals['order_id'] = [line.order_id.id, line.order_id.name]
										line_vals['product_id'] = [line.product_id.id, line.product_id.name]
										line_vals['qty'] = line.qty
										line_vals['total_qtys'] = line.qty
										line_vals['type_of_update'] = 'new'
										order_line_list.append(line_vals)
						vals['total_items'] = len(vals['lines'])
						order_list.append(vals)
			order_id['orders'] = order_list
			order_id['orderlines'] = order_line_list
			return order_id
		else:
			_logger.info('------change--%r',(changes))
			kitchen_screen_config = self.env['pos.kitchen.screen.config'].browse(data['kitchen_config_id'])
			if kitchen_screen_config:
				kitchen_screen_config.write({'is_changed':True})
			if changes:
				order_id['updated_orderlines'] = {}
				lines_by_product_id = {line.product_id.id:line for line in order.lines}
				new_lines = []
				if changes.get('new'):
					for line in changes.get('new'):
						if line.get('id') in lines_by_product_id:

							lines_by_product_id[line.get('id')].total_qtys += line.get('qty')
							if lines_by_product_id[line.get('id')].qty_added:
								lines_by_product_id[line.get('id')].qty_added += line.get("qty")
							else:
								lines_by_product_id[line.get('id')].qty_added = line.get("qty")
							if lines_by_product_id[line.get('id')].previous_quantity:
								lines_by_product_id[line.get('id')].qty_added = line.get("qty")
							if order.order_progress == 'done' or lines_by_product_id[line.get('id')].is_orderline_done:

								if order.order_progress == 'done':
									order.order_progress = 'pending' if config_id.auto_accept else 'new'

								lines_by_product_id[line.get('id')].previous_quantity = lines_by_product_id[line.get('id')].total_qtys + lines_by_product_id[line.get('id')].qty_added - lines_by_product_id[line.get('id')].qty_removed
								lines_by_product_id[line.get('id')].previous_first_quantity = lines_by_product_id[line.get('id')].qty
								lines_by_product_id[line.get('id')].qty_added = 0
								lines_by_product_id[line.get('id')].qty_removed = 0
								lines_by_product_id[line.get('id')].total_qtys = line.get('qty')
								lines_by_product_id[line.get('id')].qty = line.get('qty')
								lines_by_product_id[line.get('id')].is_orderline_done = False


						else:
							if order.order_progress == 'done':
								order.order_progress = 'pending' if config_id.auto_accept else 'new'

							new_lines.append((0,0,{'product_id':line.get('id'),'qty':line.get('qty'),'state':'in_process' if config_id.auto_accept else 'new'}))
							order.write({'lines':new_lines})
				if changes.get('cancelled'):
					for line in changes.get('cancelled'):
						if line.get('id') in lines_by_product_id:
							lines_by_product_id[line.get('id')].total_qtys -= line.get('qty')
							if lines_by_product_id[line.get('id')].qty_removed:
								lines_by_product_id[line.get('id')].qty_removed += line.get("qty")
							else:
								lines_by_product_id[line.get('id')].qty_removed = line.get("qty")
			order.is_changed = True






	def _kitchen_order_line_fields(self, line, session_id=None):
		line = [
			line[0], line[1], {k: v for k, v in line[2].items() if k in ['display_name','product_id','qty','price_unit','note','display_name','total_qtys']}
		]
		return line



class PosConfig(models.Model):
	_inherit = 'pos.config'

	# type_of_order_action = fields.Selection([('print','Print Receipt'),('show_on_kitchen','Show To Kitchen Screen'),('both',"Show And Print ")],default="show_on_kitchen")

	order_action = fields.Selection([('validation','On Order Validation'),('order_button','Clicking On Order Button')],default="order_button")

class PosOrder(models.Model):
	_inherit = "pos.order"

	order_type = fields.Selection([('pos','Point Of Sale'),('kitchen','Kitchen')],string="Order Type")
	is_kitchen_order = fields.Boolean(string="Is Kitchen Order")

"""
	@api.model
	def create_from_ui(self, orders, draft=False):
		order_ids = super(PosOrder, self).create_from_ui(orders,draft)
		for order_id in order_ids:
			order = self.env['pos.order'].browse(order_id.get('id'))
			config_id = order.config_id
			if config_id.order_action != 'validation':
				_logger.info("**********order****%r",order)
				data = order.read(['user_id','session_id','name','partner_id','date_order','amount_total','order_type'])[0]
				lines = []
				for line in order.lines.read(['display_name','product_id','qty','price_unit','note']):
					line.update({
						'total_qtys':line.get('qty'),
						'product_id':line.get('product_id')[0]
					})
					lines.append((0,0,line))
				res = {
					'user_id':      order.user_id.id or False,
					'config_id':   config_id.id,
					'session_id':   order.session_id.id,
					'lines':        lines if len(lines) else False,
					'pos_reference': order.pos_reference,
					'partner_id':   order.partner_id.id or False,
					'date_order':   order.date_order,
					'amount_total':  order.amount_total,
					'table_id':  order.table_id.id if order.table_id else False ,
					'order_type':  'kitchen',
					'floor_id':  order.table_id.floor_id.id if order.table_id else False
				}
				_logger.info("************order ref*******%r",order.pos_reference)
				# find_order = filter(lambda l:l.get('data').get('name') == order.pos_reference,orders)
				# _logger.info("*********8kitche order*******%r",list(find_order))
				# fin_order = list(find_order)
				fin_order = []
				for t_order in orders:
					_logger.info("****************order ref di name******%r",t_order.get('data').get('name'))
					if t_order.get('data') and t_order.get('data').get('name') == order.pos_reference:
						fin_order.append(t_order)
				_logger.info("********fin_order[0]***111111111*******%r",fin_order)
				if fin_order and fin_order[0]  and (fin_order[0].get('data').get('is_kitchen_order') or fin_order[0].get('data').get('token_no')):
					_logger.info("********fin_order[0]***2222*******%r",fin_order[0])
					res.update({'kitchen_order_name':fin_order[0].get('data').get('token_no'),
						'order_progress':'new'
					})
				_logger.info("********Res**********%r",res)
				order = self.env['pos.kitchen.order'].create(res)
				order_list = []
				order_line_list = []
				payment_list = []
				if(order):
					has_category_product = []
					pos_screen_data = self.env['pos.kitchen.screen.config'].search([("pos_config_ids",'=ilike',config_id.id)])
					is_allowed_order = True
					if len(pos_screen_data.pos_category_ids.ids):
						for line in order.lines:
							if not line.is_orderline_done:
								for cat in line.product_id.pos_categ_id:
									if cat.id in pos_screen_data.pos_category_ids.ids:
										has_category_product.append(line.product_id)
						if len(has_category_product) == 0:
							is_allowed_order = False
					if is_allowed_order:
						vals = {}
						vals['lines'] = []
						vals['name'] = order.name
						vals['amount_total'] = order.amount_total
						vals['pos_reference'] = order.pos_reference
						vals['table_id'] = [order.table_id.id,order.table_id.name]
						vals['floor_id'] = [order.floor_id.id,order.floor_id.name]
						vals['order_progress'] = order.order_progress
						vals['date_order'] = order.date_order
						vals['order_type'] = order.order_type
						vals['kitchen_order_name'] = order.kitchen_order_name
						if order.partner_id:
							vals['partner_id'] = [order.partner_id.id, order.partner_id.name]
						else:
							vals['partner_id'] = False
						vals['id'] = order.id
						for line in order.lines:
							if not line.is_orderline_done:
								count = 0
								for categ in line.product_id.pos_categ_id:
									if categ in pos_screen_data.pos_category_ids and not count:
										count += 1
										vals['lines'].append(line.id)
										line_vals = {}
										line_vals['display_name'] = line.display_name
										line_vals['id'] = line.id
										line_vals['order_id'] = [line.order_id.id, line.order_id.name]
										line_vals['product_id'] = [line.product_id.id, line.product_id.name]
										line_vals['qty'] = line.qty
										line_vals['total_qtys'] = line.qty
										line_vals['type_of_update'] = 'new'
										order_line_list.append(line_vals)
						vals['total_items'] = len(vals['lines'])
						order_list.append(vals)
				order_id['orders'] = order_list
				order_id['orderlines'] = order_line_list
		return order_ids
"""
