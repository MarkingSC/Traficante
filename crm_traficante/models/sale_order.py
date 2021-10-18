
import logging
from odoo import models, fields, api, exceptions, _


_logger = logging.getLogger(__name__)

class saleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        pass_flag = True
        for so in self:
            for line in so.order_line:
                _logger.debug("**** qty_available_today" + str(qty_available_today))
                _logger.debug("**** virtual_available_at_date" + str(virtual_available_at_date))
                _logger.debug("**** free_qty_today" + str(	free_qty_today))
                _logger.debug("**** product_uom_qty" + str(product_uom_qty))
                _logger.debug("**** qty_to_deliver" + str(qty_to_deliver))
                if (line.virtual_available_at_date < line.qty_to_deliver and not line.is_mto):
                    pass_flag = False
                    message = _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                              (line.qty_to_deliver, line.product_uom.name, line.product_id.name, line.virtual_available_at_date,
                               line.product_uom.name, line.order_id.warehouse_id.name)
                    raise exceptions.UserError(message)
        if pass_flag:
            result = super(saleOrder, self).action_confirm()
            return result