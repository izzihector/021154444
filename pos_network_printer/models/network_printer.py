# -*- coding: utf-8 -*-

from odoo import models, fields


class NetworkPrinter(models.Model):
    _name = 'network.printer'
    _rec_name = 'printer_name'

    printer_name = fields.Char(string="Printer name", required=True)
    printer_ip = fields.Char(string="IP Adress", required=True)
    printer_port = fields.Integer(string="Port", required=True, default=9100)
    connector_id = fields.Many2one('printer.connector', string='Connector', required=True)
