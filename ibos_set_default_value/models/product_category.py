# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    removal_strategy_id = fields.Many2one('product.removal', 'Force Removal Strategy')

    property_cost_method = fields.Selection([
        ('standard', 'Standard Price'),
        ('fifo', 'First In First Out (FIFO)'),
        ('average', 'Average Cost (AVCO)')], string="Costing Method",
        company_dependent=True, copy=True, required=True, default='average')

    property_valuation = fields.Selection([
        ('manual_periodic', 'Manual'),
        ('real_time', 'Automated')], string='Inventory Valuation',
        company_dependent=True, copy=True, required=True, default='real_time')

    # @api.model
    # def default_get(self, field):
    #     value = super(ProductCategory, self).default_get(field)
    #     product_rem = self.env['product.removal'].search([('method', '=', 'fifo')])
    #     value['removal_strategy_id'] = product_rem
    #     return value

