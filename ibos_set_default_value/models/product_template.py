# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Products(models.Model):
    _inherit = "product.template"

    detailed_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')], string='Product Type', required=True, default='product')

    available_in_pos = fields.Boolean(string='Available in POS', default=True)

    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking", required=True, default='lot')

    use_expiration_date = fields.Boolean(string='Expiration Date',
                                         help='When this box is ticked, you have the possibility to specify dates to manage'
                                              ' product expiration, on the product and on the corresponding lot/serial numbers',
                                         default=True)
