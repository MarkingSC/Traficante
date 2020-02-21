
import logging
from odoo import models, fields, api, exceptions, _


_logger = logging.getLogger(__name__)

class saleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for so in self:
            for line in so.order_line:
                if (line.virtual_available_at_date < line.qty_to_deliver and not line.is_mto):
                    message = _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                              (line.qty_to_deliver, line.product_uom.name, line.product_id.name, line.virtual_available_at_date,
                               line.product_uom.name, line.order_id.warehouse_id.name)
                    raise exceptions.UserError(message)
            else:
                result = super(saleOrder, self).action_confirm()
                return result