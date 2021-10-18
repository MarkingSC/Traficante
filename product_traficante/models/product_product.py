
import logging
from odoo import models, fields, api, _, exceptions
from datetime import timedelta, datetime

datetime.today()

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _search_qty_available(self, operator, value):
        # In the very specific case we want to retrieve products with stock available, we only need
        # to use the quants, not the stock moves. Therefore, we bypass the usual
        # '_search_product_quantity' method and call '_search_qty_available_new' instead. This
        # allows better performances.
        #if not ({'from_date', 'to_date'} & set(self.env.context.keys())):
            #product_ids = self._search_qty_available_new(
                #operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
                #self.env.context.get('package_id')
            #)
            #return [('id', 'in', product_ids)]
        #return self._search_product_quantity(operator, value, 'qty_available')
        product_ids = self._search_qty_available_new(
                operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
                self.env.context.get('package_id')
            )
        return [('id', 'in', product_ids)]

