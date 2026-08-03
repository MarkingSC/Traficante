# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # campo numerico computado(crear la funcion para el calculo), no se almacena
    qty_invoiceable = fields.Integer(string="Facturables", compute='_get_qty_invoiceable')
    consumible_ok = fields.Boolean(string='Producto consumible', default=False, store=True)
    # modifcación del tipo de producto para quitar la opción consumible y solo dejar almacenable y servicio
    type = fields.Selection(selection='_get_new_product_type', string='Product type', default='product', required=True, tracking=True,
                            help='A storable product is a product for which you manage stock. The inventory app has to be installed.\n'
                                 'A consumable product is a product for which stock is not managed.\n'
                                 'A service is a non-material product you provide.')
    @api.model
    def _get_new_product_type(self):
        selection = [
            ('product', 'Almacenable'),
            ('service', 'Servicio'),
            ('consu', 'Consumible')]
        return selection

    @api.model
    def _get_qty_invoiceable(self):
        for product in self:
            available = product.qty_available
            outgoing = product.outgoing_qty
            product.qty_invoiceable = available-outgoing

    #campo original del tipo de producto
    #type = fields.Selection([('consu', 'Consumible'),('service', 'Servicio'),('product', 'Almacenable'),], string='Tipo de Producto', required=True, default='product')