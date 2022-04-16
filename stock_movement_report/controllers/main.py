# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import io
import json
from odoo import http
from odoo.tools import html_escape
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from PyPDF2 import  PdfFileReader, PdfFileWriter

class ReportController(http.Controller):

    @http.route('/action_report_print', type='http', auth='user', methods=['POST'], csrf=False)
    def get_report_info(self, data, **kw):
        token = kw.get('csrf_token')
        data_s = json.loads(data)
        report_obj = request.env[data_s.get('model')].with_user(request.session.uid)
        return self.print_report(model=data_s.get('model'), report_obj=report_obj,token=token,options=data_s.get('options'), report_format=data_s.get('report_format'),kw=kw)

    def print_report(self, model, options, report_format,token ,report_obj=None, **kw):
        options = json.loads(options)
        report_name = report_obj.get_report_filename(options)
        report_response = False
        try:
            if report_format == 'xlsx':
                report_response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition(report_name + '.xlsx'))
                    ]
                )
                report_obj.get_xlsx(options, report_response)
            if report_format == 'pdf':
                report_response = request.make_response(
                    report_obj.get_report_pdf(options),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', content_disposition(report_name + '.pdf'))
                    ]
                )
                
            report_response.set_cookie('fileToken', token)
            return report_response
        except Exception as e:
            error_message = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': _serialize_exception(e)
            }
            return request.make_response(html_escape(json.dumps(error_message)))
