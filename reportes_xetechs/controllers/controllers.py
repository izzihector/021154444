# -*- coding: utf-8 -*-
from odoo import http

# class ReportesXetechs(http.Controller):
#     @http.route('/reportes_xetechs/reportes_xetechs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reportes_xetechs/reportes_xetechs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reportes_xetechs.listing', {
#             'root': '/reportes_xetechs/reportes_xetechs',
#             'objects': http.request.env['reportes_xetechs.reportes_xetechs'].search([]),
#         })

#     @http.route('/reportes_xetechs/reportes_xetechs/objects/<model("reportes_xetechs.reportes_xetechs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reportes_xetechs.object', {
#             'object': obj
#         })