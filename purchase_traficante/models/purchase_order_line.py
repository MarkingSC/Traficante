
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.model
    def _get_received_date(self):
        stock_move = self.order_id.picking_ids[0]
        if stock_move:
            self.received_date = stock_move.date_done
        else:
            self.received_date = None

    receipt_type = fields.Selection(selection = [('regular','Regular'),('credito','Crédito'),('consigna','Consigna')], string='Tipo de recepción', default="regular", required=True)

    partner_id = fields.Many2one(string="Proveedor", comodel_name="res.partner", related="order_id.partner_id")
    received_date = fields.Date(string="Fecha de recepción", default=_get_received_date)

   