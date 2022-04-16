# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _
import json


class ProductLot(models.Model):
	_inherit = 'stock.production.lot'

	def _default_expiry_date(self):
		self.expiration_date.date() if self.expiration_date else False

	@api.onchange('expiration_date')
	def onc_expiration_date(self):
		self.expiry_date = self.expiration_date.date() if self.expiration_date else False

	@api.depends('name','product_id.barcode')
	def _compute_lot_name(self):
		for rec in self:
			rec.lot_name = ''
			if rec.barcode :
				rec.lot_name = str(rec.barcode) +'/'+ rec.name
			else:
				rec.lot_name = rec.name

	product_tmpl_id =fields.Many2one('product.template', string='Product Template',related ='product_id.product_tmpl_id')
	lot_name = fields.Char("Lot Name",compute="_compute_lot_name")
	barcode = fields.Char('Barcode',related ='product_id.barcode')
	expiration_date = fields.Datetime(string='Expiration Date')
	expiry_date =  fields.Date(string='Expiry Date', default=lambda self: self._default_expiry_date())
	product_qty = fields.Float('Quantity', compute='_product_qty',store=True)

	avail_locations = fields.Many2many('stock.location',string="Available locations",
		compute="_compute_avail_locations")
	quant_text = fields.Text('Quant Qty',compute='_compute_avail_locations')
	list_price = fields.Float('Sales Price', store=True)

	@api.depends('quant_ids','quant_ids.location_id','quant_ids.quantity')
	def _compute_avail_locations(self):
		for rec in self:
			rec.avail_locations = []
			locations = rec.quant_ids.filtered(lambda x: x.quantity > 0 and x.location_id.usage == 'internal').mapped('location_id')
			rec.avail_locations = [(6,0,locations.ids)]
			rec.quant_text = ''
			aa = dict(zip(
				(rec.quant_ids.filtered(lambda x: x.quantity > 0 and x.location_id.usage == 'internal').mapped('location_id.id')),
				(rec.quant_ids.filtered(lambda x: x.quantity > 0 and x.location_id.usage == 'internal').mapped('quantity'))
				))
			rec.quant_text = json.dumps(aa)

class Product(models.Model):
	_inherit = "product.product"

	barcode_ids = fields.One2many('stock.production.lot','product_id',
		string='Barcodes Lots')

	def checkProductQuantity(self, product_id, config_id):
		config = self.env['pos.config'].search([('id', '=', config_id)])
		products = self.env['product.product'].search([('id', '=', product_id)])
		stock_qtn = self.env['stock.quant'].search([('product_id', '=', products.id)])
		for stc in stock_qtn:
			if products.id == stc.product_id.id:
				if stc.location_id.id == config.picking_type_id.default_location_src_id.id:
					if stc.quantity > 0:
						return 2; # return 2 is product quantity is available in pos
					else:
						return 3; # return 3 is product quantity is not available in pos
			else:
				return 1# return 1 if product location and pos_config warehouse location is not same
		return 0 # return 0 if product has no stock location

	def checkIfLotAvailable(self, product, config, lotName):
		config = self.env['pos.config'].search([('id', '=', config)])
		products = self.env['product.product'].search([('id', '=', product)])
		stock_qtn = self.env['stock.quant'].search([('product_id', '=', products.id)])
		for stc in stock_qtn:
			if products.id == stc.product_id.id:
				if stc.location_id.id == config.picking_type_id.default_location_src_id.id:
					if stc.lot_id.name == lotName:
						return 1
		return 0


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	barcode_ids = fields.One2many(related='product_variant_ids.barcode_ids')
	is_lot_seleted = fields.Boolean(default=False)

	@api.model
	def create(self, vals):
		res = super(ProductTemplate, self).create(vals)
		if res.tracking != 'none':
			res.list_price = 0.00
			res.is_lot_seleted = True
		return res

	@api.onchange('tracking')
	def _onchange_tracking(self):
		if self.tracking == 'none':
			self.is_lot_seleted = False
		if self.tracking != 'none':
			self.list_price = 0.00
			self.is_lot_seleted = True

	def write(self, vals):
		return super(ProductTemplate, self).write(vals)

class pos_config(models.Model):
	_inherit = 'pos.config'

	show_stock_location = fields.Selection([('all', 'All Locations'),
		('specific', 'Operation Type Location')],default='all',string='Select Lots from')

	op_typ_loc_id = fields.Many2one('stock.location', string='Operation Type Location',
		related='picking_type_id.default_location_src_id')

class posOrder(models.Model):
	_inherit = 'pos.order'

	def _order_fields(self, ui_order):
		order = super(posOrder, self)._order_fields(ui_order)
		# parent_order = self.search([('pos_reference', '=', ui_order['name'])], limit=1)
		# updated_lines = ui_order['lines']
		#
		# for uptd in updated_lines:
		# 	# print('uptd->mrp', uptd[2]['mrp_unit'])
		# 	line = self.env['pos.order.line'].search([('order_id', '=', parent_order.id)], limit=1)
		# 	for lot_barcode in uptd[2]['lots_barcode']:
		# 		if line:
		# 			line.mrp_unit = lot_barcode['mrp_unit']
		return order

class posOrderLine(models.Model):
	_inherit = 'pos.order.line'

	mrp_unit = fields.Char('MRP')

	def _order_line_fields(self, line, session_id=None):
		orderline = super(posOrderLine, self)._order_line_fields(line, session_id)
		if len(line[2]['lots_barcode']) == 1:
			lot_barcode = line[2]['lots_barcode'][0]
			lineDict = orderline[2]
			lineDict['mrp_unit'] = lot_barcode['mrp_unit']
			orderline[2] = lineDict
			return orderline
		return orderline


