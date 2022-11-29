import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = 'account.move'

    def calculate_discount(self):
        _logger.info('**** entra a calculate_discount: ')
        self.discount = 0
        no_decimales = self.currency_id.no_decimales
        no_decimales_prod = self.currency_id.decimal_places

        # Itera las lineas de factura
        for line in self.invoice_line_ids:

            price_wo_discount = line.price_unit * (1 - (line.discount / 100.0))
            # Busca los impuestos incluidos en el precio
            taxes_prod = line.tax_ids.compute_all(price_wo_discount, currency=line.currency_id, quantity=line.quantity, product=line.product_id, partner=line.move_id.partner_id,)
            tax_included = 0
            for taxes in taxes_prod['taxes']:
                tax = self.env['account.tax'].browse(taxes['id'])
                if tax.impuesto != '004':
                    if tax.price_include or tax.amount_type == 'division':
                        tax_included += taxes['amount']


            # Obtiene monto final del descuento considerando impuestos incluidos en el precio
            total_wo_discount = round(line.price_unit * line.quantity - tax_included, no_decimales_prod)
            discount_prod = round(total_wo_discount - line.price_subtotal, no_decimales_prod) if line.discount else 0
            self.discount += discount_prod

        self.discount = round(self.discount, no_decimales)
        _logger.info('**** self.discount: ' + str(self.discount))


    def write(self, vals):
        
        res = super(AccountMove, self).write(vals)

        if 'invoice_line_ids' in vals or 'amount_untaxed' in vals:
            self.calculate_discount()
        
        return res
        

    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        res.calculate_discount()
        return res