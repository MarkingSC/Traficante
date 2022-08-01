import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
class productTemplate(models.Model):
    _inherit = 'product.template'

    latest_cost = fields.Float(string='Latest Cost', compute = "_get_product_cost", compute_sudo=True)
    avg_cost = fields.Float(string='Average Cost', compute = "_get_product_cost", compute_sudo=True)
    ieps_tax_pct = fields.Float(string='IVA Pct.', compute = "_get_taxes_amount")
    iva_tax_pct = fields.Float(string='IEPS Pct', compute = "_get_taxes_amount")
    iva_price = fields.Float(string='Price, IVA included', compute = "_get_taxes_amount")
    ieps_cost = fields.Float(string='Cost, IEPS included', compute = "_get_taxes_amount")
    taxes_cost = fields.Float(string='Cost, taxes included', compute = "_get_taxes_amount")
    # En el reporte en este orden va standard_price
    taxes_price = fields.Float(string='Price, taxes included', compute = "_get_taxes_amount")
    total_margin_amt = fields.Float(string='Margin amount', compute = "_get_margins", store = True)
    cost_margin_pct = fields.Float(string='Margin over cost', compute = "_get_product_cost", store = True, compute_sudo=True)
    price_margin_pct = fields.Float(string='Margin on price', compute = "_get_product_cost", store = True, compute_sudo=True)

    # Margen del precio sobre el costo del producto
    product_cost = fields.Float(string='Cost')
    price_margin = fields.Float(string='Margin', store = True)
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.",
        readonly = True)
    standard_price = fields.Float(
        'Price', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the last unit that left the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""", readonly = True)

    @api.onchange('price_margin', 'product_cost', 'taxes_id')
    def _get_product_price(self):
        _logger.info('**** inicio _get_product_price *****')   
        self.standard_price = (self.product_cost * (1 + self.price_margin))
        new_price = self.env['stock.change.standard.price'].with_context(active_model = 'product.template', active_id = self.id).create({'new_price': self.standard_price})
        _logger.info('**** new_standard_price: ' + str (new_price))
        _logger.info('**** new_price: ' + str (new_price))
        _logger.info('**** new_price: ' + str (new_price.new_price))
        new_price.change_price()
        taxes = 0
        taxes_res = self.taxes_id.compute_all(
            self.standard_price, 
            self.company_id.currency_id,
            1, 
            self)
            
        _logger.info('**** taxes_res: ' + str(taxes_res))
        for tax_res in taxes_res['taxes']:
            taxes += tax_res['amount']

        _logger.info('**** taxes: ' + str(taxes))
        self.list_price = self.standard_price + taxes

    def write(self, vals):

        _logger.info('**** inicio write *****')
        _logger.info('**** vals: ' + str(vals))
        
        res = super(productTemplate, self).write(vals)

        if 'price_margin' in vals or 'product_cost' in vals or 'taxes_id' in vals:
            self.standard_price = (self.product_cost * (1 + self.price_margin))
            new_price = self.env['stock.change.standard.price'].with_context(active_model = 'product.template', active_id = self.id).create({'new_price': self.standard_price})
            _logger.info('**** new_standard_price: ' + str (new_price))
            _logger.info('**** new_price: ' + str (new_price))
            _logger.info('**** new_price: ' + str (new_price.new_price))
            new_price.change_price()
            taxes = 0
            taxes_res = self.taxes_id.compute_all(
                self.standard_price, 
                self.company_id.currency_id,
                1, 
                self)
                
            _logger.info('**** taxes_res: ' + str(taxes_res))
            for tax_res in taxes_res['taxes']:
                taxes += tax_res['amount']

            _logger.info('**** taxes: ' + str(taxes))
            self.list_price = self.standard_price + taxes

        _logger.info('**** fin write *****')
        return res

    def _get_product_cost(self):
        _logger.info('**** inicio _get_product_cost *****')
        for product in self:

            # ultimo costo
            latest_purchase_line = self.env['purchase.order.line'].search([('product_id', '=', product.id)], limit = 1, order='date_planned desc')
            _logger.info('**** latest_purchase_line: ' + str(latest_purchase_line.order_id.name))
            if latest_purchase_line:
                if latest_purchase_line.product_cost:
                    product.latest_cost = latest_purchase_line.product_cost
                else
                    latest_purchase_line.get_cost_from_product()
                    product.latest_cost = latest_purchase_line.product_cost
            else:
                product.latest_cost = 0

            purchase_lines = self.env['purchase.order.line'].search([('product_id', '=', product.id)])
            sum_cost = 0
            
            # costo promedio
            for line in purchase_lines:
                sum_cost += line.price_unit

            if len(purchase_lines) > 0:
                product.avg_cost = sum_cost/len(purchase_lines)
            else:
                product.avg_cost = 0

        _logger.info('**** fin _get_product_cost *****')
            
    @api.depends('latest_cost', 'taxes_id', 'standard_price')
    def _get_taxes_amount(self):
        _logger.info('**** inicio _get_taxes_amount *****')

        for product in self:

            latest_cost = product.latest_cost
            quantity = 1
            
            # Porcentaje de IEPS y ieps_cost
            ieps_taxes = product.taxes_id.filtered(lambda tax: tax.tax_group_id.ieps_section == True)       

            total_ieps = 0     

            for tax in ieps_taxes:
                    compute_all_res = tax.compute_all(latest_cost, product.company_id.currency_id, quantity, product, False, False, handle_price_include=True)
                    #compute_all_res_2 = tax.compute_all(latest_cost, product.company_id.currency_id, quantity, product, False, False, handle_price_include=False)

                    for calc_tax in compute_all_res['taxes']:
                        total_ieps += calc_tax['amount']

                    #for calc_tax in compute_all_res_2['taxes']:
                    #    total_ieps_cost += calc_tax['amount']

            ieps_amount = total_ieps

            if product.latest_cost:
                product.ieps_tax_pct = ieps_amount / product.latest_cost
                product.ieps_cost = product.latest_cost + ieps_amount
            else:
                product.ieps_tax_pct = 0
                product.ieps_cost = 0

            # Porcentaje de IVA e iva_price
            iva_taxes = product.taxes_id.filtered(lambda tax: tax.tax_group_id.iva_section == True)      
            iva_price = 0      

            if len(iva_taxes) > 1:
                raise ValidationError(_('Product %s has more than one IVA tax.')%(product.name))
            
            for tax in iva_taxes:
                computed_iva = tax.compute_all(product.standard_price, product.company_id.currency_id, quantity, product, False, False, handle_price_include=False)
                
                _logger.info('**** computed_iva: ' + str(computed_iva))
                for calc_tax in computed_iva['taxes']:
                    iva_price += calc_tax['amount']

            if product.standard_price:
                product.iva_tax_pct = iva_price / product.standard_price
                product.iva_price = product.standard_price + iva_price
            else:
                product.iva_tax_pct = 0
                product.iva_price = 0

            # Costo con impuestos = Costo con IEPS más IVA
            product.taxes_cost = product.ieps_cost * (1+product.iva_tax_pct)

            # Precio con impuestos = Standard price + IEPS + IVA
            product.taxes_price = (product.standard_price * (1+product.ieps_tax_pct)) * (1+product.iva_tax_pct)

        _logger.info('**** fin _get_taxes_amount *****')


    @api.depends('taxes_price', 'taxes_cost', 'taxes_price')
    def _get_margins(self):
        _logger.info('**** inicio _get_margins *****')

        for product in self:
            # margen bruto
            product.total_margin_amt = product.taxes_price - product.taxes_cost

            # margen sobre el costo
            if product.taxes_cost:
                product.cost_margin_pct = product.total_margin_amt / product.taxes_cost
            else:
                product.cost_margin_pct = 0

            # margen sobre el precio
            if product.taxes_price:
                product.price_margin_pct = product.total_margin_amt / product.taxes_price 
            else:
                product.price_margin_pct = 0

        _logger.info('**** fin _get_margins *****')

    @api.onchange('standard_price')
    def _get_margins_on_sp(self):
        _logger.info('**** inicio _get_margins_on_sp *****')
        self._get_product_cost()
        self._get_taxes_amount()
        self._get_margins()
        _logger.info('**** inicio _get_margins_on_sp *****')

