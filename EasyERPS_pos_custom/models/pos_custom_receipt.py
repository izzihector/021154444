# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'


    pos_custom_receipt= fields.Boolean('Custom Receipt', default=True)
    show_company_contact_address = fields.Boolean(string='Show Company Contact Address', help="Enables Show Company Contact Address.", default=True)
    show_company_phone = fields.Boolean(string='Show Company Phone', help="Enables Show Company Phone.", default=True)
    show_company_email = fields.Boolean(string='Show Company Email', help="Enables how Company Email.", default=True)
    show_company_website = fields.Boolean(string='Show Company Website', help="Show Company Website.", default=True)
    show_qr_code = fields.Boolean(string="Show QR Code in Receipt", default=True)


    leftpane_width = fields.Integer(string="left Pane Width", default="500")
    product_name_font_size = fields.Integer(string="Product Name Font Size", default="12")
    category_name_font_size = fields.Integer(string="Category Name Font Size", default="12")

class POSOrder(models.Model):
    _inherit = 'pos.order'

    order_refunded = fields.Char(string="Order Refunded", required=False, )

    @api.model
    def create(self, values):
        res = super(POSOrder, self).create(values)
        if len(res.refunded_order_ids) != 0:
            res.order_refunded = ','.join(res.refunded_order_ids.mapped('pos_reference'))
        return res