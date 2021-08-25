
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _validatePartnerData(self, partners):
        _logger.debug("**** INICIA _validatePartnerData")
        # Campos requeridos en el cliente para continuar con el pedido
        reqFields = ['vat', 'start_delivery_time', 'finish_delivery_time', 'bank_ids','street', 'street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']

        validFieldsFlag = True

        #partner_invoice_id
        #partner_shipping_id
        _logger.debug("**** reqFields: " + str(reqFields))
        for partner in partners:
            _logger.debug("**** ITERA EL PARTNER: " + partner.id)
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                _logger.debug("**** EVALUANDO EL CAMPO: " + reqField)
                if partner[reqField] is None:
                    _logger.debug("**** NO SE ENCONTRÓ EL CAMPO")
                    validFieldsFlag = False

                _logger.debug("**** validFieldsFlag: " + validFieldsFlag)
                
            if validFieldsFlag:
                _logger.debug("**** ACTUALIZA EL CLIENTE CON CUSTOMER_TYPE A")
                self.env['res.partner'].write({'customer_type', 'A'})

        _logger.debug("**** FINALIZA _validatePartnerData")
        return validFieldsFlag
            
                
    @api.model
    def create(self, vals):

        # Obtiene el objeto del cliente asociado al pedido
        partnerInvId = self.partner_invoice_id.id
        partnerShipId = self.partner_shipping_id.id
        partnerInv = self.partner_invoice_id
        partnerShip = self.partner_shipping_id


        #partnerInv = self.env['res.partner'].search([('customer_type','=', 'P'), ('id', '=', partnerInvId)])
        #partnerInv = self.env['res.partner'].search([('id', '=', partnerInvId)])
        #partnerShip = self.env['res.partner'].search([('customer_type','=', 'P'), ('id', '=', partnerShipId)])
        #partnerShip = self.env['res.partner'].search([('id', '=', partnerShipId)])

        validInvPartner = self._validatePartnerData(partnerInv)
        validShipPartner = self._validatePartnerData(partnerShip)

        if not validInvPartner:
            raise exceptions.UserError("Capture todos los datos requeridos para la dirección de facturación.")
        if not validShipPartner:
            raise exceptions.UserError("Capture todos los datos requeridos para la dirección de entrega.")

        # Si todo sale bien guarda el pedido
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        for order in self:
            if 'partner_invoice_id' in vals:
                #partnerInvId = self.partner_invoice_id.id
                #partnerInv = self.env['res.partner'].search([('customer_type','=', 'P'), ('id', '=', partnerInvId)])
                partnerInv = self.partner_invoice_id
                #partnerInv = self.env['res.partner'].search([('id', '=', partnerInvId)])
                validInvPartner = self._validatePartnerData(partnerInv)

                if not validInvPartner:
                    raise exceptions.UserError("Capture todos los datos requeridos para la dirección de facturación.")
            
            if 'partner_shipping_id' in vals:
                #partnerShipId = self.partner_shipping_id.id
                #partnerShip = self.env['res.partner'].search([('customer_type','=', 'P'), ('id', '=', partnerShipId)])
                #partnerShip = self.env['res.partner'].search([('id', '=', partnerShipId)])
                partnerShip = self.partner_shipping_id
                validShipPartner = self._validatePartnerData(partnerShip)

                if not validShipPartner:
                    raise exceptions.UserError("Capture todos los datos requeridos para la dirección de entrega.")
            

        return super(SaleOrder, self).write(vals)
        
 
