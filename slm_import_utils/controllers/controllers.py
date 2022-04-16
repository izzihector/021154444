# -*- coding: utf-8 -*-
from odoo import http

# class SlmImportUtils(http.Controller):
#     @http.route('/slm_import_utils/slm_import_utils/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/slm_import_utils/slm_import_utils/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('slm_import_utils.listing', {
#             'root': '/slm_import_utils/slm_import_utils',
#             'objects': http.request.env['slm_import_utils.slm_import_utils'].search([]),
#         })

#     @http.route('/slm_import_utils/slm_import_utils/objects/<model("slm_import_utils.slm_import_utils"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('slm_import_utils.object', {
#             'object': obj
#         })