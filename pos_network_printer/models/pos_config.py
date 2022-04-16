# -*- coding: utf-8 -*-

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    ticket_print_mode = fields.Selection([('web', 'Web'), ('network', 'Network')], string='Ticket print mode', default='web', required=True)
    bill_print_mode = fields.Selection([('web', 'Web'), ('network', 'Network')], string='Bill print mode', default='web', required=True)
    network_printer_ids = fields.Many2many('network.printer', string='Network printers')
    printing_mode = fields.Selection([('offline', 'Offline'), ('online', 'Online')], string='Printing mode', default='offline',
                                     required=True)
    connector = fields.Selection([('jspm', 'JsPrintManager'), ('websocket', 'Websocket'), ('printc', 'Printer Connector')],
                                 string='Connector', default='jspm')
    client_app_ip = fields.Char(string='Client App IP')
    client_app_port = fields.Char(string='Client App Port', default=24443)
