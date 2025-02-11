import logging
from odoo import api, fields, models, exceptions, _

_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def button_validate(self):
        _logger.info("**** mb_stock_lot_validation.button_validate con self.id: " + str(self.id))

        for line in self.move_line_ids:

            stock_quant = self.env['stock.quant'].search([
                ('company_id','=',self.company_id.id),
                ('location_id','=',line.location_id.id),
                ('product_id','=',line.product_id.id),
                ('lot_id','=',line.lot_id.name)])

            _logger.info("**** stock_quant: " + str(stock_quant))
            _logger.info("**** stock_quant.id: " + str(stock_quant.id))

            _logger.info("**** line.qty_done: " + str(line.qty_done))
            _logger.info("**** stock_quant.quantity: " + str(stock_quant.quantity))

            if  (stock_quant.id == False or line.qty_done > stock_quant.quantity) and self.picking_type_id.code != 'incoming':
                if line.lot_id.id == False:
                    raise exceptions.UserError("No existen cantidades suficientes en la ubicación de origen para el producto " + str(line.product_id.display_name))
                else:    
                    raise exceptions.UserError("No existen cantidades suficientes del lote especificado en la ubicación de origen para el producto " + str(line.product_id.display_name))
            
        res = super(StockPicking, self).button_validate()
        
        _logger.info('**** TERMINA button_validate *****')
        
        return res