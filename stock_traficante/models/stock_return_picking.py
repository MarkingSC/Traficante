import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import pytz
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    reason_return = fields.Selection([('recibo', 'Recibo equivocado'), ('refacturacion', 'Refacturación')],
                                     string='Motivo de la devolución', required=True, default='recibo')
    return_detail = fields.Text(string='Detalle de la devolución', required=False)

    def _create_returns(self):
        new_picking, pick_type_id = super(StockReturnPicking, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        #_logger.info("**** Valor de new_picking: " + str(new_picking))
        #_logger.info("**** Valor de pick_type_id: " + str(pick_type_id))
        #_logger.info("**** Valor de picking: " + str(picking))
        picking.write({'is_return': True,
                       'reason_return': self.reason_return,
                       'return_detail': self.return_detail})
        return new_picking, pick_type_id
