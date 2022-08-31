import logging
from odoo import models, fields, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = 'account.move'

    ieps_taxes = fields.Many2many(
        comodel_name = 'account.tax',
        relation = 'account_tax_ieps_account_move_rel',
        string = 'IEPS', compute = "_get_taxes_amount", store=True)
    ieps_amount = fields.Float(string='IEPS amount', compute = "_get_taxes_amount", store=True)
    ieps_percent= fields.Float(string='IEPS Pct.', compute = "_get_taxes_amount", store=True, digits=(16, 4))

    iva_taxes = fields.Many2many(
        comodel_name = 'account.tax',
        relation = 'account_tax_iva_account_move_rel',
        string = 'IVA', compute = "_get_taxes_amount", store=True)
    iva_amount = fields.Float(string='IVA amount', compute = "_get_taxes_amount", store=True)

    customer_vat = fields.Char(string='Customer vat', related='partner_id.vat')

    @api.depends('line_ids')
    def _get_taxes_amount(self):
        for record in self:
            _logger.info('**** _get_taxes_amount para a factura: ' + str(record))
            
            list_ieps_taxes = record.invoice_line_ids.mapped('ieps_taxes')
            _logger.info('**** list_ieps_taxes: ' + str(list_ieps_taxes))

            list_ieps_amount = record.invoice_line_ids.mapped('ieps_amount')
            _logger.info('**** list_ieps_amount: ' + str(list_ieps_amount))

            list_iva_taxes = record.invoice_line_ids.mapped('iva_taxes')
            _logger.info('**** list_iva_taxes: ' + str(list_iva_taxes))

            list_iva_amount = record.invoice_line_ids.mapped('iva_amount')
            _logger.info('**** list_iva_amount: ' + str(list_iva_amount))

            ieps_taxes = list_ieps_taxes
            _logger.info('**** ieps_taxes: ' + str(ieps_taxes))

            ieps_amount = sum(list_ieps_amount)
            _logger.info('**** ieps_amount: ' + str(ieps_amount))

            if record.amount_untaxed_signed > 0:
                ieps_percent = ieps_amount/record.amount_untaxed_signed
            else:
                ieps_percent = 0
            _logger.info('**** ieps_percent: ' + str(ieps_percent))
            
            iva_taxes = list_iva_taxes
            _logger.info('**** iva_taxes: ' + str(iva_taxes))

            iva_amount = sum(list_iva_amount)
            _logger.info('**** iva_amount: ' + str(iva_amount))

            record.ieps_taxes = ieps_taxes
            record.ieps_amount = ieps_amount
            record.ieps_percent = ieps_percent
            record.iva_taxes = iva_taxes
            record.iva_amount = iva_amount

        _logger.info('**** termina _get_taxes_amount: ')
