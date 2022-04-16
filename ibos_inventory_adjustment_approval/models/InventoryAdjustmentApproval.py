# -*- coding: utf-8 -*-from odoo import api, fields, models
from odoo import api, fields, models, _


class InventoryAdjustmentApproval(models.Model):
    _inherit = "stock.quant"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('apply', 'Apply'),
        ('set', 'Set'),
        ('clear', 'Clear')],
        string='Status', default="draft")

    def action_submit_to_manager(self):
        self.state = 'submitted'
        if self.state == 'submitted':
            print("Yes")

    def action_apply_inventory(self):
        self.state = 'apply'
        res = super(InventoryAdjustmentApproval, self).action_apply_inventory()
        return res

    def action_set_inventory_quantity(self):
        self.state = 'set'
        res = super(InventoryAdjustmentApproval, self).action_set_inventory_quantity()
        return res

    def action_set_inventory_quantity_to_zero(self):
        self.state = 'clear'
        res = super(InventoryAdjustmentApproval, self).action_set_inventory_quantity_to_zero()
        return res



