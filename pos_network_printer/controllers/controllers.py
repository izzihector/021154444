# -*- coding: utf-8 -*-
from odoo import http
from ..xmlescpos import printer
import json
import logging


class NetworkPrinter(http.Controller):
    @http.route('/print-network-xmlreceipt', auth='user', method=['POST'], type='json', csrf=False)
    def print_network_xmlreceipt(self, printer_ip, printer_port, uid, **kw):
        try:
            try:
                imp = printer.Network(printer_ip, printer_port)
                imp.receipt(kw.get('receipt'))
                imp.__del__()
                return json.dumps({'error': 0, 'uid': uid})
            except WindowsError as error:
                logging.error(error)
                return json.dumps({'error': 0})
            except Exception as error:
                logging.error(error)
                return json.dumps({'error': 1, 'uid': uid})
        except NameError:
            try:
                imp = printer.Network(printer_ip, printer_port)
                imp.receipt(kw.get('receipt'))
                imp.__del__()
                return json.dumps({'error': 0, 'uid': uid})
            except Exception as error:
                logging.error(error)
                return json.dumps({'error': 1, 'uid': uid})


    @http.route('/check-printer', auth='user', method=['POST'], type='json', crsf=False)
    def check_printer(self, printer_ip, printer_port, **kw):
        try:
            try:
                imp = printer.Network(printer_ip, printer_port)
                imp.__del__()
                return json.dumps({'error': 0})
            except WindowsError as error:
                logging.error(error)
                return json.dumps({'error': 0})
            except Exception as error:
                logging.error(error)
                return json.dumps({'error': 1})
        except NameError:
            try:
                imp = printer.Network(printer_ip, printer_port)
                imp.__del__()
                return json.dumps({'error': 0})
            except Exception as error:
                logging.error(error)
                return json.dumps({'error': 1})


    @http.route('/check-all-printer', auth='user', method=['POST'], type='json', crsf=False)
    def check_all_printer(self, ids, **kw):
        try:
            try:
                printer_obj = http.request.env['network.printer']
                for item in ids:
                    current_printer = printer_obj.browse(item)
                    imp = printer.Network(current_printer.printer_ip, current_printer.printer_port)
                    imp.__del__()
                return json.dumps({'error': 0})
            except WindowsError as error:
                logging.error(error)
                return json.dumps({'error': 0})
            except Exception as error:
                logging.error(error)
                return json.dumps({'error': 1})
        except NameError:
            try:
                printer_obj = http.request.env['network.printer']
                for item in ids:
                    current_printer = printer_obj.browse(item)
                    imp = printer.Network(current_printer.printer_ip, current_printer.printer_port)
                    imp.__del__()
                return json.dumps({'error': 0})
            except Exception as error:
                logging.error(error)
                return json.dumps({'error': 1})