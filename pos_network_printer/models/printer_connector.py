# -*- coding: utf-8 -*-

from odoo import models, fields, api
import secrets


class PrinterConnector(models.Model):
    _name = 'printer.connector'

    name = fields.Char(string='Name', required=True)
    token = fields.Char(string='Token', required=False)
    order_printer_ids = fields.One2many('network.printer', 'connector_id', string='Printers')
    kitchen_printer_ids = fields.One2many('restaurant.printer', 'connector_id', string='Orders Printers')

    @api.model
    def create(self, values):
        values.update({'token': secrets.token_hex(16)})
        return super(PrinterConnector, self).create(values)
