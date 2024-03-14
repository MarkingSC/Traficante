# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    # campo numerico computado(crear la funcion para el calculo), no se almacena
    qty_invoiceable = fields.Float(string="Cantidad facturable", compute='_get_qty_invoiceable')
    product_location = fields.Char(string="Ubicación", compute='_get_product_location', store=True)
    total_sale = fields.Float(string="Total ventas", compute='_get_total_sale')
    total_purchase = fields.Float(string="Total compras", compute='_get_total_purchase')

    def _get_qty_invoiceable(self):
        for product in self:
            available = product.qty_available
            outgoing = product.outgoing_qty
            product.qty_invoiceable = available-outgoing

    @api.depends('default_code')
    def _get_product_location(self):  # función para obtener la ubicación del producto
        for product in self:
            if product.default_code:
                locations = self.env['stock.quant'].search([('product_id', '=', product.default_code)])
                if locations:
                    product_locations = [loc.location_id.complete_name for loc in locations]
                    product.product_location = ", ".join(product_locations)
                else:
                    product.product_location = "No hay ubicaciones disponibles"

    def _get_total_sale(self):
        for product in self:
            price = product.lst_price
            quantity = product.qty_invoiceable
            product.total_sale = price * quantity

    def _get_total_purchase(self):
        for product in self:
            price = product.standard_price
            quantity = product.qty_invoiceable
            product.total_purchase = price * quantity