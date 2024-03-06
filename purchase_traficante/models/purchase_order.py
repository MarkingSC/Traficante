
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

    #logica para ocultar el boton editar de las ordenes de compra, el field se agrega en la vista form
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)

    @api.depends('state')
    def _compute_css(self):
        for record in self:
            if record.state != 'draft':
                record.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.test_css = False