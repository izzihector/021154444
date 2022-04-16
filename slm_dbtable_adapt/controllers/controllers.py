# -*- coding: utf-8 -*-
from odoo import http

# class SlmDbtableAdapt(http.Controller):
#     @http.route('/slm_dbtable_adapt/slm_dbtable_adapt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/slm_dbtable_adapt/slm_dbtable_adapt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('slm_dbtable_adapt.listing', {
#             'root': '/slm_dbtable_adapt/slm_dbtable_adapt',
#             'objects': http.request.env['slm_dbtable_adapt.slm_dbtable_adapt'].search([]),
#         })

#     @http.route('/slm_dbtable_adapt/slm_dbtable_adapt/objects/<model("slm_dbtable_adapt.slm_dbtable_adapt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('slm_dbtable_adapt.object', {
#             'object': obj
#         })