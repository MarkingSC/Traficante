import logging
from odoo import models, fields, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_file = fields.Binary(string='Invoice document')
    partner_business_name = fields.Char(string='Razón social', related="partner_id.business_name")
    partner_commercial_name = fields.Char(string='Nombre Comercial', compute='_get_client_name', store=True)
    #partner_commercial_name = fields.Char(string='Nombre Comercial')

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        return super(AccountMove, self.sudo()).message_post(**kwargs)

    @api.depends('invoice_origin', 'partner_id')
    def _get_client_name(self):
        _logger.info('**** entra a _get_client_name: ')
        self.ensure_one()
        if self.invoice_origin:
            _logger.info('**** origen de la factura: ' + str(self.invoice_origin))
            sale_order_origin = self.env['sale.order'].search([('name', '=', self.invoice_origin)], limit = 1)
            sale_partner_name = sale_order_origin.partner_id.name
            _logger.info('**** nombre del cliente: ' + str(sale_partner_name))
            self.partner_commercial_name = sale_partner_name
