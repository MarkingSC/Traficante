# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_qty_invoiceable(self):
        for product in self:
            available = product.qty_available
            outgoing = product.outgoing_qty
            product.qty_invoiceable = available-outgoing

    # campo numerico computado(crear la funcion para el calculo), no se almacena
    qty_invoiceable = fields.Integer(string="Facturables", compute=_get_qty_invoiceable)
