
import logging
from odoo import models, fields, api, exceptions, _


_logger = logging.getLogger(__name__)

class saleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        pass_flag = True
        for so in self:
            for line in so.order_line:
                #_logger.debug("**** qty_available_today" + str(line.qty_available_today)) #Usando esta variable se contempla la cantidad en stock sin restar las reservadas
                #_logger.debug("**** virtual_available_at_date" + str(line.virtual_available_at_date)) #Usando esta variable se contempla la cantidad en previstas (stock + entradas - salidas)
                #_logger.debug("**** free_qty_today" + str(line.free_qty_today)) #Usando esta variable solo se contemplan las cantidades que están 100% libres, es decir, stock a mano menos reservadas para pedidos
                if (line.free_qty_today < line.qty_to_deliver and not line.is_mto):
                    pass_flag = False
                    message = _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                              (line.qty_to_deliver, line.product_uom.name, line.product_id.name, line.free_qty_today,
                               line.product_uom.name, line.order_id.warehouse_id.name)
                    raise exceptions.UserError(message)
        if pass_flag:
            result = super(saleOrder, self).action_confirm()
            return result