# -*- coding: utf-8 -*-
from odoo import http

# class SlmEncryptionReports(http.Controller):
#     @http.route('/slm_encryption_reports/slm_encryption_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/slm_encryption_reports/slm_encryption_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('slm_encryption_reports.listing', {
#             'root': '/slm_encryption_reports/slm_encryption_reports',
#             'objects': http.request.env['slm_encryption_reports.slm_encryption_reports'].search([]),
#         })

#     @http.route('/slm_encryption_reports/slm_encryption_reports/objects/<model("slm_encryption_reports.slm_encryption_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('slm_encryption_reports.object', {
#             'object': obj
#         })