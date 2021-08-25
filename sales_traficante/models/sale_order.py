
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _validateMainPartnerData(self, partners):
        _logger.debug("**** INICIA _validateMainPartnerData")
        reqFields = ['vat', 'start_delivery_time', 'finish_delivery_time', 'bank_ids','street']
        validFieldsFlag = True

        _logger.debug("**** reqFields: " + str(reqFields))
        for partner in partners:
            _logger.debug("**** ITERA EL PARTNER: " + str(partner.id))
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                _logger.debug("**** EVALUANDO EL CAMPO: " + str(reqField))
                _logger.debug("**** partner[reqField]" + str(partner[reqField]))
                if not partner[reqField]:
                    _logger.debug("**** NO SE ENCONTRÓ EL CAMPO")
                    validFieldsFlag = False

                _logger.debug("**** validFieldsFlag: " + str(validFieldsFlag))
                
            if validFieldsFlag:
                _logger.debug("**** ACTUALIZA EL CLIENTE CON CUSTOMER_TYPE A")
                self.env['res.partner'].write({'customer_type', 'A'})

        _logger.debug("**** FINALIZA _validateMainPartnerData")
        return validFieldsFlag


    def _validateAddrPartnerData(self, partners):
        _logger.debug("**** INICIA _validateAddrPartnerData")
        # Campos requeridos en el cliente para continuar con el pedido
        reqFields = ['street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']

        validFieldsFlag = True

        _logger.debug("**** reqFields: " + str(reqFields))
        for partner in partners:
            _logger.debug("**** ITERA EL PARTNER: " + str(partner.id))
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                _logger.debug("**** EVALUANDO EL CAMPO: " + str(reqField))
                _logger.debug("**** partner[reqField]" + str(partner[reqField]))
                if not partner[reqField]:
                    _logger.debug("**** NO SE ENCONTRÓ EL CAMPO")
                    validFieldsFlag = False

                _logger.debug("**** validFieldsFlag: " + str(validFieldsFlag))

            # No lo actualiza porque estas son solo direcciones  
            #if validFieldsFlag:
            #    _logger.debug("**** ACTUALIZA EL CLIENTE CON CUSTOMER_TYPE A")
            #    self.env['res.partner'].write({'customer_type', 'A'})

        _logger.debug("**** FINALIZA _validateAddrPartnerData")
        return validFieldsFlag
            
                
    @api.model
    def create(self, vals):
        
        if 'partner_id' in vals:
            _logger.debug("**** GUARDANDO partner_id ")
            partnerMain = vals['partner_id']
            validInvPartner = self._validateAddrPartnerData(partnerInv)
            if not validInvPartner:
            raise UserError("Capture todos los datos requeridos para la dirección de facturación.")
        if 'partner_invoice_id' in vals:
            _logger.debug("**** GUARDANDO partner_invoice_id ")
            partnerInv = vals['partner_invoice_id']
            validShipPartner = self._validateAddrPartnerData(partnerShip)
            if not validShipPartner:
            raise UserError("Capture todos los datos requeridos para la dirección de entrega.")
        if 'partner_shipping_id' in vals:
            _logger.debug("**** GUARDANDO partner_shipping_id ")
            partnerShip = vals['partner_shipping_id']
            validMainPartner = self._validateMainPartnerData(partnerMain)
            if not validMainPartner:
            raise UserError("Capture todos los datos requeridos para el cliente.")

        # Si todo sale bien guarda el pedido
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        for order in self:
            if 'partner_invoice_id' in vals:
                partnerInv = self.partner_invoice_id
                validInvPartner = self._validateAddrPartnerData(partnerInv)

                if not validInvPartner:
                    raise UserError("Capture todos los datos requeridos para la dirección de facturación.")
            
            if 'partner_shipping_id' in vals:
                partnerShip = self.partner_shipping_id
                validShipPartner = self._validateAddrPartnerData(partnerShip)

                if not validShipPartner:
                    raise UserError("Capture todos los datos requeridos para la dirección de entrega.")

            if 'partner_id' in vals:
                partnerMain = self.partner_id
                validMainPartner = self._validateMainPartnerData(partnerMain)

                if not validMainPartner:
                    raise UserError("Capture todos los datos requeridos para el cliente.")
            

        return super(SaleOrder, self).write(vals)
        
 
