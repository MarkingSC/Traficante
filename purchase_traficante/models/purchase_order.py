
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    receipt_type = fields.Selection(selection = [('regular','Regular'),('credito','Crédito'),('consigna','Consigna')], string='Tipo de recepción', default="regular", required=True)
        
    @api.onchange('receipt_type')
    def _onchange_receipt_type(self):
        self.payment_term_id = None

    @api.model
    def create(self, vals):
        if 'receipt_type' in vals:
            for line in self.order_line:
                line.receipt_type = vals['receipt_type']

        # Si todo sale bien guarda la orden de compra
        return super(PurchaseOrder, self).create(vals)