
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.onchange('name')
    def update_sales_price(self):
        _logger.info('**** Entra a update_sales_price con: ' + str(self.standard_price))
        #
        #for product in self:
        #    _logger.info('****  product[standard_price]: ' + str(product['standard_price']))
        #    company = self.env.company.id
        #    res = self.env['product.pricelist']._get_partner_pricelist_multi([], company_id=company)
        #    _logger.info('****  type(res): ' + str(type(res)))
        #    _logger.info('****  list(res.keys())[0]: ' + str(list(res.keys())[0]))
        #    price = product.with_context(pricelist=res.id, uom=product.uom_id.id).price
        #    _logger.info('****  price: ' + str(price))
        #    
        #    for price in prices:
        #        _logger.info('****  price: ' + str(price))
