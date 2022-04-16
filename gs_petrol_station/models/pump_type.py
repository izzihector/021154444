# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class GSPumpType(models.Model):
    _name = 'gs.pump.type'
    _description = 'Pump Type'

    name = fields.Char(string='Name', )
    product_id = fields.Many2one('product.product', string='Product')
