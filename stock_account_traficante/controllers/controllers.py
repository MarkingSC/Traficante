# -*- coding: utf-8 -*-
# from odoo import http


# class StockTraficante(http.Controller):
#     @http.route('/stock_traficante/stock_traficante/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_traficante/stock_traficante/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_traficante.listing', {
#             'root': '/stock_traficante/stock_traficante',
#             'objects': http.request.env['stock_traficante.stock_traficante'].search([]),
#         })

#     @http.route('/stock_traficante/stock_traficante/objects/<model("stock_traficante.stock_traficante"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_traficante.object', {
#             'object': obj
#         })
