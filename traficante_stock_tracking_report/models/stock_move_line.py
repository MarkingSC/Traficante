from datetime import date, datetime
from itertools import product
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
class stockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    # Fecha de entrada del lote
    lot_incoming_date = fields.Date(string='Lot incoming date')
    # días de inventario o tiempo de inactividad (desde la entrada del lote)
    lot_iddle_time = fields.Integer(string='Iddle time')
    # costo del producto movido
    lot_product_cost = fields.Float(string='Product cost')
    # stock restante
    lot_current_stock = fields.Integer(string='Stock', group_operator=False)
    # tipo de operación
    lot_picking_type = fields.Many2one('stock.picking.type', string='Picking type')
    # tipo de operación
    lot_origin_doc = fields.Char(string='Origin document')
    # tipo de operación
    lot_incoming_qtty = fields.Integer(string='Incoming')
    # tipo de operación
    lot_outgoing_qtty = fields.Integer(string='Outgoing')
    # usuario responsable
    lot_uid = fields.Many2one('res.users', string='User')


class stockPicking(models.Model):
    _inherit = 'stock.picking'

    # Cuando se actualice el movimiento a 'Hecho' se asociarán los datos
    def write(self, vals):
        _logger.info('**** ENTRA A write de  stockPicking con vals: ' + str(vals))

        res = super(stockPicking, self).write(vals)

        _logger.info('**** self.state: ' + str(self.state))
        
        if 'date_done' in vals and self.state == 'done':
            _logger.info('**** Entra a obtener los datos de la líena de lote *****')
            self._get_lines_lot_data()            
            
        _logger.info('**** TERMINA write de  stockPicking *****')
        return res

    def _get_lines_lot_data(self):
        _logger.info('**** ENTRA A _get_lines_lot_data ***** ')
        for lot_line in self.move_ids_without_package.move_line_ids.filtered(lambda x: x.lot_id != False):
            # Obtener la fecha de entrada del lote
            lot_incoming_line = self.env['stock.move.line'].search([
                ('picking_id.picking_type_id.code', '=', 'incoming'), 
                ('state', '=', 'done'), 
                ('lot_id', '=', lot_line.lot_id.id)
            ])
            lot_line.lot_incoming_date = lot_incoming_line.date

            # Obtener días de inventario
            today = datetime.today()
            lot_line.lot_iddle_time = (today-lot_incoming_line.date).days 

            # Obtener costo del producto
            lot_line.lot_product_cost = lot_line.product_id.product_cost

            # Obtener existencias 
            lot_line.lot_current_stock = lot_line.product_id.qty_available

            # Obtener el tipo de movimiento 
            lot_line.lot_picking_type = lot_line.picking_id.picking_type_id

            # Obtener el origen del movimiento 
            lot_line.lot_origin_doc = lot_line.picking_id.origin

            # Obtener cantidad de entradas
            if lot_line.lot_picking_type.code == 'incoming':
                lot_line.lot_incoming_qtty = lot_line.qty_done
            elif lot_line.lot_picking_type.code == 'outgoing':
                lot_line.lot_outgoing_qtty = lot_line.qty_done        

            # Obtener el usuario encargado
            lot_line.lot_uid = self.env.user

        _logger.info('**** ENTRA A _get_lines_lot_data ***** ')
