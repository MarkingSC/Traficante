
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    receipt_type = fields.Selection(selection = [('regular','Regular'),('credito','Crédito'),('consigna','Consigna')], string='Tipo de recepción', default="regular", required=True)

    @api.onchange('payment_term_id')
    def _onchange_payment_term(self):
        """ Si se cambian los plazos de pago y es un plazo con dias de crédito entonces se toma como recepción a crédito.
        """

        payment_term = self.env['account.payment.term'].search([('id', '=', self.payment_term_id.id)])
        if payment_term:
            if len(payment_term.line_ids) == 1 and payment_term.line_ids[0].days == 0:
                self.receipt_type = 'regular'
            elif self.receipt_type != 'consigna':
                self.receipt_type = 'credito'
        
    @api.depends('receipt_type')
    def _evaluate_payment_type(self):
        for record in self:
            _logger.debug("**** inicia _evaluate_payment_type para la orden: " + str(record))
            payment_term = self.env['account.payment.term'].search([('id', '=', record.payment_term_id)])
            if payment_term:
                _logger.debug("**** plazo de pago seleccionado: " + str(payment_term.name))
                _logger.debug("**** tipo de recepción seleccionada: " + str(record.receipt_type))
                if len(payment_term.line_ids) == 1 and payment_term.line_ids[0].days == 0:
                    if record.receipt_type != 'regular':
                        raise UserError("No es posible generar la orden de compra. Si el plazo de pago inmediato la recepción debe ser regular.")
                elif record.receipt_type != 'credito':
                        raise UserError("No es posible generar la orden de compra. Si el plazo de pago no es inmediato la recepción debe ser a crédito.")
            
    @api.model
    def create(self, vals):
        if 'receipt_type' in vals:
            for line in self.order_line:
                line.receipt_type = vals['receipt_type']

        # Si todo sale bien guarda la orden de compra
        return super(PurchaseOrder, self).create(vals)