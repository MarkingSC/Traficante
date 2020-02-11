# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseTraficante(http.Controller):
#     @http.route('/purchase_traficante/purchase_traficante/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_traficante/purchase_traficante/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_traficante.listing', {
#             'root': '/purchase_traficante/purchase_traficante',
#             'objects': http.request.env['purchase_traficante.purchase_traficante'].search([]),
#         })

#     @http.route('/purchase_traficante/purchase_traficante/objects/<model("purchase_traficante.purchase_traficante"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_traficante.object', {
#             'object': obj
#         })
