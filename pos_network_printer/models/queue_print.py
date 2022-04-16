# -*- coding: utf-8 -*-

from odoo import models, fields, api


class QueuePrint(models.Model):
    _name = 'queue.print'
    _rec_name = 'connector_id'

    connector_id = fields.Many2one('printer.connector', string='Connector', required=True)
    printer_name = fields.Char(string="Printer name", required=True)
    printer_ip = fields.Char(string="IP Adress", required=True)
    printer_port = fields.Integer(string="Port", required=True)
    receipt = fields.Char(string='Receipt', required=True)
    state = fields.Selection([('new', 'New'), ('printed', 'Printed')], string='State', default='new', required=True)
    token = fields.Char(string='Token', required=True)
