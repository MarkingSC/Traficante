

import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import calendar
import pytz
from odoo.exceptions import AccessError, UserError, ValidationError

datetime.today()

_logger = logging.getLogger(__name__)

class salesOrigin(models.Model):
    _name = 'sales.origin'
    _description = 'Sales origin'

    # nombre del registro del origen de ventas
    name = fields.Char(string='Name', required=True, help='Set the name of the origin.')
    # descripcion del registro del origen de ventas
    description = fields.Char(string='Description', required=True, help='Set the description.')

class resPartner(models.Model):
    _inherit = 'res.partner'

    # Origen de venta para reportes
    sales_origin_id = fields.Many2one(string='Sales type', help='Optionally specify a sales type for reporting', comodel_name='sales.origin')

class saleOrder(models.Model):
    _inherit = 'sale.order'


    # Origen de venta para reportes
    sales_origin_id = fields.Many2one(string='Sales type', help='Optionally specify a sales type for reporting', comodel_name='sales.origin')
    
    @api.onchange('partner_id')
    def _get_sales_origin(self):
        _logger.info('**** ENTRA A onchange _get_sales_origin *****')   
        for order in self:
            order.sales_origin_id = order.partner_id.sales_origin_id

    def write(self, values):
        """Override default Odoo write function and extend."""
        # Do your custom logic here
        _logger.info('**** ENTRA A write para setar el sales origin de las FACTURAS *****')   

        res = super(saleOrder, self).write(values)

        if 'sales_origin_id' in values:

            invoices = self.env['account.move'].search([
                        ('journal_id.type', '=', 'sale'), 
                        ('invoice_origin', '=', self.name)])

            _logger.info('**** Facturas del pedido: ' + str (invoices))   

            for invoice in invoices:
                _logger.info('**** invoice.name: ' + str(invoice.name))
                invoice.sales_origin_id = self.sales_origin_id

        return res

class accountMove(models.Model):
    _inherit = 'account.move'

    # Origen de venta para reportes
    sales_origin_id = fields.Many2one(string='Sales type', help='Optionally specify a sales type for reporting', comodel_name='sales.origin')

    @api.model
    def create(self, values):
        _logger.info('**** ENTRA A create para setar el sales origin de la factura *****')   
        res = super(accountMove, self).create(values)
        sale_order = self.env['sale.order'].search([('name', '=', res.invoice_origin)], limit = 1)
        _logger.info('**** sale_order: ' +str(sale_order))  
        res.sales_origin_id = sale_order.sales_origin_id
        return res

    def write(self, values):
        """Override default Odoo write function and extend."""
        # Do your custom logic here
        _logger.info('**** ENTRA A write para setar el sales origin de las lineas *****')   

        res = super(accountMove, self).write(values)

        if 'sales_origin_id' in values:
            for line in self.invoice_line_ids:
                _logger.info('**** line: ' + str(line))
                line.sales_origin_id = self.sales_origin_id

        return res

class accountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_sales_origin(self):
        return [(line.id, line.move_id.sales_origin_id) for line in self]

    # Origen de venta para reportes
    sales_origin_id = fields.Many2one(string='Sales type', help='Optionally specify a sales type for reporting', comodel_name='sales.origin', default=_get_sales_origin)