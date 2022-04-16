# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

                   
class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    contract_product_ids = fields.Many2many("product.template", string='ID Productos', compute="_get_contract_product_ids")
    
    @api.depends('item_ids')
    def _get_contract_product_ids(self):
        for order in self:
            product_list = []
            for product in order.item_ids:
                if order.item_ids.product_tmpl_id:
                    product_list.append(product.product_tmpl_id.id) 
            order.contract_product_ids = product_list