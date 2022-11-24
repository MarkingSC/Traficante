import logging
from odoo import models, fields, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_code = fields.Char(string='Product Code', compute = "_get_product_code")
    product_name = fields.Char(string='Product Name', compute = "_get_product_name")
    product_cost = fields.Float(string='Product Cost', compute = "_get_product_cost")

    move_id_state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')
        ], string='Status', related='move_id.state', readonly=True)

    move_id_estado_factura = fields.Selection(
        selection=[('factura_no_generada', 'Factura no generada'), ('factura_correcta', 'Factura correcta'), 
                   ('solicitud_cancelar', 'Cancelación en proceso'),('factura_cancelada', 'Factura cancelada'),
                   ('solicitud_rechazada', 'Cancelación rechazada')],
        string='Estado de factura', related='move_id.estado_factura',
        readonly=True)

    business_name = fields.Char(string='Business Name', related='partner_id.business_name', store=True)
    commercial_name = fields.Char(string='Commercial Name', related='partner_id.name', store=True)
    salesperson = fields.Char(string='Salesperson', related='move_id.invoice_user_id.name', store=True)

    ieps_taxes = fields.Many2many(
        'account.tax',
        'ieps_tax_move_lines',
        'move_line_id',
        'account_tax_id',
        'IEPS', compute = "_get_taxes_amount", store=True)
    ieps_amount = fields.Float(string='IEPS amount', compute = "_get_taxes_amount", store=True)
    ieps_percent= fields.Float(string='IEPS Pct.', compute = "_get_taxes_amount", store=True, digits=(16, 4))

    iva_taxes = fields.Many2many(
        'account.tax',
        'iva_tax_move_lines',
        'move_line_id',
        'account_tax_id',
        'IVA', compute = "_get_taxes_amount", store=True)
    iva_amount = fields.Float(string='IVA amount', compute = "_get_taxes_amount", store=True)

    # Este campo es solo para tener el dato del descuento en decimales.
    discount_pct = fields.Float(string='Discount Pct.', compute = "_get_discount_pct", store=False)
    

    @api.depends('discount')
    def _get_discount_pct(self):
        _logger.info('**** entra a _get_discount_pct ***** ')
        for record in self:
            if record.discount:
                record.discount_pct = record.discount/100
            else:
                record.discount_pct = 0
        _logger.info('**** termina _get_discount_pct ***** ')

    @api.depends('product_id')
    def _get_product_code(self):
        _logger.info('**** entra a _get_product_code ***** ')
        _logger.info('**** total lineas: ' + str(len(self)))
        for record in self:
            if record.product_id:
                record.product_code = record.product_id.default_code
        _logger.info('**** termina _get_product_code ***** ')

    @api.depends('product_id')
    def _get_product_name(self):
        _logger.info('**** entra a _get_product_name: ')
        for record in self:
            if record.product_id:
                record.product_name = record.product_id.name
        _logger.info('**** termina _get_product_name: ')

    @api.depends('product_id')
    def _get_product_cost(self):
        _logger.info('**** entra a _get_product_cost: ')
        for record in self:
            if record.product_id:
                product_cost_pp = record.product_id.standard_price
                qtty = record.quantity
                record.product_cost = product_cost_pp * qtty
        _logger.info('**** termina _get_product_cost: ')

    @api.depends('product_id')
    def _get_taxes_amount(self):
        for record in self:
            _logger.info('**** _get_taxes_amount para a linea: ' + str(record))
            if record.product_id != False:

                #### IEPS
                ieps_taxes = record.tax_ids.filtered(lambda tax: tax.tax_group_id.ieps_section == True)

                total_ieps = 0
                price_unit = record.price_unit
                quantity = record.quantity
                product = record.product_id
                customer = record.partner_id

                for tax in ieps_taxes:
                    compute_all_res = tax.compute_all(price_unit, record.currency_id, quantity, product, customer, False, handle_price_include=True)
                    
                    for calc_tax in compute_all_res['taxes']:
                        total_ieps += calc_tax['amount']

                record.ieps_amount = total_ieps
                record.ieps_taxes = ieps_taxes

                if record.price_subtotal:
                    record.ieps_percent = record.ieps_amount / record.price_subtotal
                else:
                    record.ieps_percent = 0

                #### IVA
                iva_taxes = record.tax_ids.filtered(lambda tax: tax.tax_group_id.iva_section == True)

                total_iva = 0
                base_amount = (record.price_unit * record.quantity) + total_ieps
                price_unit = record.price_unit
                quantity = record.quantity
                product = record.product_id
                customer = record.partner_id

                for tax in iva_taxes:
                    compute_all_res = tax.compute_all(base_amount, record.currency_id, 1, product, customer, False, handle_price_include=True)

                    for calc_tax in compute_all_res['taxes']:
                        total_iva += calc_tax['amount']

                record.iva_amount = total_iva
                record.iva_taxes = iva_taxes

                if record.id == 25516:
                    _logger.info('**** record.id: ' + str(record.id))
                    _logger.info('**** record.iva_amount: ' + str(record.iva_amount))
                    _logger.info('**** compañía de la línea: ' + str(record.company_id.name))

        _logger.info('**** termina _get_taxes_amount: ')
