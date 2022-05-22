from cgitb import reset
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_cost = fields.Float(string='Product cost')
    list_price = fields.Float(string='Sales Price')
    standard_price = fields.Float(string='Price')

    @api.model
    def create(self, vals):
        _logger.info('**** inicio create en PurchaseOrderLine*****')
        _logger.info('**** vals: ' + str(vals))

        res = super(PurchaseOrderLine, self).create(vals)

        if 'product_id' in vals:

            _logger.info('**** product_id: ' + str(vals['product_id']))
            _logger.info('**** res.product_id: ' + str(res.product_id))
            _logger.info('**** res.product_id.product_cost: ' + str(res.product_id.product_cost))

            res.product_cost = res.product_id.product_cost
            res.list_price = res.product_id.list_price
            res.standard_price = res.product_id.standard_price

        _logger.info('**** fin create en PurchaseOrderLine*****')
        return res


    def write(self, vals):

        _logger.info('**** inicio write en PurchaseOrderLine*****')
        _logger.info('**** vals: ' + str(vals))
        
        res = super(PurchaseOrderLine, self).write(vals)

        if 'product_id' in vals:
            self.product_cost = self.product_id.product_cost
            self.list_price = self.product_id.list_price
            self.standard_price = self.product_id.standard_price

        _logger.info('**** fin write en PurchaseOrderLine*****')
        return res