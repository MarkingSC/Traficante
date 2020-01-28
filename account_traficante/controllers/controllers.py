# -*- coding: utf-8 -*-
# from odoo import http


# class AccountTraficante(http.Controller):
#     @http.route('/account_traficante/account_traficante/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_traficante/account_traficante/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_traficante.listing', {
#             'root': '/account_traficante/account_traficante',
#             'objects': http.request.env['account_traficante.account_traficante'].search([]),
#         })

#     @http.route('/account_traficante/account_traficante/objects/<model("account_traficante.account_traficante"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_traficante.object', {
#             'object': obj
#         })
