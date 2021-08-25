
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _validatePartnerData(partners):
        # Campos requeridos en el cliente para continuar con el pedido
        reqFields = ['vat', 'start_delivery_time', 'finish_delivery_time', 'bank_ids','street', 'street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']

        validFieldsFlag = True

        #partner_invoice_id
        #partner_shipping_id

        for partner in partners:
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                if partner[reqField] is None:
                    validFieldsFlag = False

            if validFieldsFlag:
                self.env['res.partner'].write({'customer_type', 'A'})
        return validFieldsFlag
            
                
    @api.model
    def create(self, vals):

        # Obtiene el objeto del cliente asociado al pedido
        partnerInvId = self.partner_invoice_id.id
        partnerShipId = self.partner_shipping_id.id

        partnerInv = self.env['res.partner'].search([('customer_type','=', 'P'), ('id', '=', partnerInvId)])
        partnerShip = self.env['res.partner'].search([('customer_type','=', 'P'), ('id', '=', partnerShipId)])

        validInvPartner = self._validatePartnerData(partnerInv)
        validShipPartner = self._validatePartnerData(partnerShip)

        if not validInvPartner:
            raise exceptions.UserError("Capture todos los datos requeridos para la dirección de facturación.")
        if not validShipPartner:
            raise exceptions.UserError("Capture todos los datos requeridos para la dirección de entrega.")

        # Si todo sale bien guarda el pedido
        return super(SaleOrder, self).create(values)

    def write(self, vals):
        for order in self:
            if 'partner_invoice_id' in vals:
                partnerInvId = self.partner_invoice_id.id
                partnerInv = self.env['res.partner'].search([('customer_type','=', 'P'), ('id', '=', partnerInvId)])
                validInvPartner = self._validatePartnerData(partnerInv)

                if not validInvPartner:
                    raise exceptions.UserError("Capture todos los datos requeridos para la dirección de facturación.")
            
            if 'partner_shipping_id' in vals:
                partnerShipId = self.partner_shipping_id.id
                partnerShip = self.env['res.partner'].search([('customer_type','=', 'P'), ('id', '=', partnerShipId)])
                validShipPartner = self._validatePartnerData(partnerShip)

                if not validShipPartner:
                    raise exceptions.UserError("Capture todos los datos requeridos para la dirección de entrega.")
            

        return super(SaleOrder, self).write(values)
        
 
