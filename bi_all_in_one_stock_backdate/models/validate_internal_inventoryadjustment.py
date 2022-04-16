# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date, timedelta
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

# class InventoryLineInherit(models.Model):
# 	_inherit = 'stock.inventory.line'

# 	transfer_remark7 = fields.Char('Remark')

# class StockInventoryInherit(models.Model):
# 	_inherit = 'stock.inventory'

# 	def action_validate_custom(self):
# 		return {
# 					'name':'Process Backdate and Remarks',
# 					'view_type': 'form',
# 					'view_mode': 'form',
# 					'res_model': 'wizard.inventory.adjustment',
# 					'type': 'ir.actions.act_window',
# 					'target': 'new',
# 					'res_id': False,
# 					'context': {
# 						'inv_id': self.id,
# 					}
# 				}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

