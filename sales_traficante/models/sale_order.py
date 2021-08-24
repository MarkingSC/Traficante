
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _validatePartnerInvDelivData(partners):
        # Campos requeridos en el cliente para continuar con el pedido
        reqInvDelivFields = ['street', 'street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']
        reqFields = ['vat', 'start_delivery_time', 'finish_delivery_time', 'bank_ids']

        validInvDelivFlag = True
        validFieldsFlag = True

        for partner in partners:
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                if partner[reqField] is None:
                    validFieldsFlag = False

            # Revisa si cuenta con todos los campos de facturación y entrega requeridos
            for reqInvDelivField in reqInvDelivFields:
                if partner[reqInvDelivField] is None:
                    validInvDelivFlag = False

            # Si no tiene todos los campos de facturación y entrega entonces busca direcciones asociadas
            if not validInvDelivFlag:
                # obtiene las direcciones de facturación y entrega registradas para el cliente
                invAddresses = self.env['res.partner'].search([('parent_id', '=', partner.id), ('type', '=', 'invoice')])
                delivAddresses = self.env['res.partner'].search([('parent_id', '=', partner.id), ('type', '=', 'delivery')])
                _logger.debug("///// DIRECCIONES DE FACTURACION DEL CLIENTE invAddress: " + invAddresses)
                _logger.debug("///// DIRECCIONES DE ENTREGA DEL CLIENTE delivAddresses: " + delivAddresses)

                # Si no hay alguno de los dos tipos de direcciones
                if len(pinvAddresses) == 0 or len(delivAddresses) == 0:
                    validFieldsFlag = False

            if validFieldsFlag:
                self.env['res.partner'].write({'customer_type', 'A'})
        return validFieldsFlag
            
                


    @api.model
    def create(self, values):

        # Obtiene el objeto del cliente asociado al pedido
        partnerId = values.get('partner_id')
        partners = self.env['res.partner'].search([('customer_type','=', 'P'), ('partner_id', '=', partner_id)])

        validFieldsFlag = self._validatePartnerInvDelivData(partners)

        if not validFieldsFlag:
            raise exceptions.UserError("Capture todos los datos del cliente requeridos para facturación.")

            # Si todo sale bien guarda el pedido
        return super(SaleOrder, self).create(values)

    def write(self, values):
        for order in self:
            if 'partner_id' in values:
                partners = self.env['res.partner'].search([('customer_type','=', 'P'), ('partner_id', '=', values.get('partner_id'))])
                validFieldsFlag = self._validatePartnerInvDelivData(partners)

                if not validFieldsFlag:
                    raise exceptions.UserError("Capture todos los datos del cliente requeridos para facturación.") 

        return super(SaleOrder, self).write(values)
        
 
