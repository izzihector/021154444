# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ContractClient(models.Model):
    _name = 'sale.contract.client'
    # _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    #_inherit = 'timer.mixin'
    _description = 'Contract information of client'
    
    name = fields.Char(string='No. de contrato', required=True, 
        copy=False, readonly=True, index=True, 
        default=lambda s: s.env['ir.sequence'].next_by_code('sale.contract.client') )
    name_of_contract = fields.Char(string='Nombre de contrato')
    partner_id = fields.Many2one("res.partner", string='Cliente', store=True, readonly=False)
    user_id = fields.Many2one("res.users", string='Usuario Responsable', store=True, readonly=False)
    type_contract = fields.Selection([('corporativo','Corporativo'),('asociaciones','Asociaciones'),('fidelidad','Planes de Fidelidad'),('individual','Individual'),('puntos_corporativos','Puntos Corporativos')], string="Tipo de contrato")
    date_assign = fields.Datetime(string='Fecha de Inicio', index=True, copy=False, default=datetime.now())
    date_closed = fields.Datetime(string='Fecha de Finalizacion', index=True, copy=False, default=datetime.now())
    price_ids = fields.Many2one("product.pricelist", string="Lista de Precios")
    planned_date = fields.Datetime(string='Fecha de entrega')
    invoice_date = fields.Datetime(string='Fecha de facturación')
    cut_date = fields.Datetime(string='Fecha de corte')
    user_portal_ids = fields.Many2many('res.users', string='Usuarios del Portal')
    vendor_id = fields.Many2one("res.users", string="Vendedor")
    rsc_id = fields.Many2one("res.users",string="RSC")
    property_payment_term_id = fields.Many2one("account.payment.term", string="Plazos de pago", readonly=False)
#     product_ids = fields.Many2many("product.product", string="Productos")
    product_ids = fields.One2many(related="price_ids.item_ids", string="Productos", readonly=False)

    # Administración Productos Propios
    amount_base_pp = fields.Float("Monto Base")
    factor_pp = fields.Float("Factor %")
    factor_urgent_pp = fields.Float("Factor Urgente %")

    # Productos de Transferencia
    amount_base_pt = fields.Float("Monto Base")
    factor_pt = fields.Float("Factor %")
    factor_urgent_pt = fields.Float("Factor Urgente %")


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for res in self:
            if res.partner_id.property_payment_term_id:
                res.property_payment_term_id = res.partner_id.property_payment_term_id