# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date, timedelta
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
				
class WizardInventoryAdjustment(models.TransientModel):
	_name = 'wizard.inventory.adjustment'

	inventory_date = fields.Datetime('Inventory BackDate',required=True)
	inventory_remark = fields.Char('Remark',required=True)	

	def button_inventory_adjust(self):
		if self.inventory_date >= datetime.now():
			raise UserError(_('Please Enter Correct Back Date'))

		if self._context.get('inv_id'):
			custom_stock_inventory_ids = self.env['stock.inventory'].browse(self._context.get('inv_id'))
			custom_stock_inventory_ids.write({
					'state':'confirm'
					})			
			custom_stock_inventory_ids.with_context(inventory_date=self.inventory_date).action_validate()
			for custom_stock_inventory_ids1 in custom_stock_inventory_ids:
				custom_stock_inventory_ids1.write({'accounting_date':self.inventory_date})
				# for custom_stock_inventory_ids3 in custom_stock_inventory_ids1.line_ids:
				# 	custom_stock_inventory_ids3.write({'transfer_remark7':self.inventory_remark})
				for custom_stock_inventory_ids2 in custom_stock_inventory_ids1.move_ids:
					custom_stock_inventory_ids2.with_context(inventory_date=self.inventory_date).write({'date':custom_stock_inventory_ids1.accounting_date,
						'move_remark':self.inventory_remark})
					for custom_stock_inventory_ids4 in custom_stock_inventory_ids2.move_line_ids:
						custom_stock_inventory_ids4.write({'date':custom_stock_inventory_ids2.date,
							'line_remark':self.inventory_remark})
						for category in custom_stock_inventory_ids2.product_id.categ_id:
							if category.property_valuation != 'real_time':
								custom_accountmove = self.env['account.move'].create({'date':self.inventory_date,
									'journal_id':custom_stock_inventory_ids2.product_id.categ_id.property_stock_journal.id,
									'stock_move_id':custom_stock_inventory_ids2.id})




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: