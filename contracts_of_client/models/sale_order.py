# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # contract_id = fields.Many2one('sale.contract.client', string="No. Contrato", domain="[('partner_id', '=', partner_id)]")
    contract_id = fields.Many2one('sale.contract.client', string="No. Contrato")
    commitment_date = fields.Datetime(string='Fecha de entrega', related='contract_id.planned_date', readonly=False)


    @api.onchange('contract_id')
    def onchange_contract_id(self):
        for res in self:
            if res.contract_id:
                if res.contract_id.partner_id:
                    res.partner_id = res.contract_id.partner_id 
                if res.contract_id.property_payment_term_id:
                    res.payment_term_id = res.contract_id.property_payment_term_id 
                if res.contract_id.price_ids:
                    res.pricelist_id = res.contract_id.price_ids
                if res.contract_id.vendor_id:
                    res.user_id = res.contract_id.vendor_id 


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    contract_product_ids = fields.Many2many(related="order_id.pricelist_id.contract_product_ids", string='ID Productos')