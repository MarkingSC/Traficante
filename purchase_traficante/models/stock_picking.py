import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import pytz
from odoo.exceptions import AccessError, UserError, ValidationError

datetime.today()

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # product return information
    is_return = fields.Boolean(string="Devolución de productos", default=False)
    reason_return = fields.Selection([('recibo', 'Recibo equivocado'),('refacturacion', 'Refacturación')],
                                     string='Motivo de la devolución', required=True, default='recibo')
    return_detail = fields.Text(string='Detalle de la devolución', required=False)