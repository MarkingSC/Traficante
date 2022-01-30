
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Se define la acción de devolución
    def action_reverse_automatic(self):
        _logger.info('**** Entra a action_reverse_automatic **** ')
        return_picking_wizard = self.env['stock.return.picking'].create({
            'picking_id': self.id
        })
        return_picking_wizard._onchange_picking_id()
        return_picking_response = return_picking_wizard.create_returns()
        _logger.info('**** Movimiento de devolución generado:' + str(return_picking_response) + ' *****') 
        return_picking = self.env['stock.picking'].search([('id', '=', return_picking_response['res_id'])], limit = 1)
        _logger.info('**** Grupo para los usuarios asignados *****' + str(self.env.ref('sales_traficante.group_stock_return_assigned')))
        _logger.info('**** Usuarios asignados *****' + str(self.env.ref('sales_traficante.group_stock_return_assigned').users[0]))
        return_picking.user_id = self.env.ref('sales_traficante.group_stock_return_assigned').users[0]

