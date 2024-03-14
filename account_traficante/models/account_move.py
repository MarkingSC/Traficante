import logging
from odoo import models, fields, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_file = fields.Binary(string='Invoice document')
    partner_business_name = fields.Char(string='Razón social', related="partner_id.business_name")
    partner_commercial_name = fields.Char(string='Nombre Comercial', compute='_get_client_name', store=True)
    #partner_commercial_name = fields.Char(string='Nombre Comercial')
    original_order_amount = fields.Float(string="Monto Factura Origen", compute='_compute_original_order_amount')
    original_invoice_date = fields.Date(string="Fecha CFDI Relacionado", compute='_compute_original_invoice_date')

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        return super(AccountMove, self.sudo()).message_post(**kwargs)

    @api.depends('invoice_origin', 'partner_id')
    def _get_client_name(self):
        _logger.info('**** entra a _get_client_name: ')
        #self.ensure_one()
        for invoice in self:
            if invoice.invoice_origin:
                _logger.info('**** origen de la factura: ' + str(invoice.invoice_origin))
                sale_order_origin = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)], limit = 1)
                sale_partner_name = sale_order_origin.partner_id.name
                _logger.info('**** nombre del cliente: ' + str(sale_partner_name))
                invoice.partner_commercial_name = sale_partner_name

    @api.depends('invoice_origin')
    def _compute_original_order_amount(self):   # función para obtener el monto de factura origen a la que pertenece cada nota de crédito
        _logger.info('**** entra a _compute_original_order_amount: ')
        for move in self:
            if move.invoice_origin:
                original_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                move.original_order_amount = original_order.amount_total if original_order else 0.0

    @api.depends('uuid_relacionado')
    def _compute_original_invoice_date(self):   # función para obtener la fecha de factura origen a la que pertenece cada nota de crédito
        _logger.info('**** entra a _get_invoice_date: ')
        for move in self:
            if move.uuid_relacionado:
                original_invoice = self.env['account.move'].search(
                    [('folio_fiscal', '=', move.uuid_relacionado), ('type', '=', 'out_invoice')], limit=1)
                if original_invoice:
                    move.write({'original_invoice_date': original_invoice.invoice_date})
                else:
                    move.write({'original_invoice_date': False})
            else:
                move.write({'original_invoice_date': False})