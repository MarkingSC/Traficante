# -*- coding: utf-8 -*-
# from odoo import http


# class CrmTraficante(http.Controller):
#     @http.route('/crm_traficante/crm_traficante/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_traficante/crm_traficante/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_traficante.listing', {
#             'root': '/crm_traficante/crm_traficante',
#             'objects': http.request.env['crm_traficante.crm_traficante'].search([]),
#         })

#     @http.route('/crm_traficante/crm_traficante/objects/<model("crm_traficante.crm_traficante"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_traficante.object', {
#             'object': obj
#         })
