# -*- coding: utf-8 -*-
# from odoo import http


# class ResPartnerTraficante(http.Controller):
#     @http.route('/res_partner_traficante/res_partner_traficante/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/res_partner_traficante/res_partner_traficante/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('res_partner_traficante.listing', {
#             'root': '/res_partner_traficante/res_partner_traficante',
#             'objects': http.request.env['res_partner_traficante.res_partner_traficante'].search([]),
#         })

#     @http.route('/res_partner_traficante/res_partner_traficante/objects/<model("res_partner_traficante.res_partner_traficante"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('res_partner_traficante.object', {
#             'object': obj
#         })
