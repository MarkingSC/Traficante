
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _validateMainPartnerData(self, partners):
        _logger.info("**** INICIA _validateMainPartnerData")
        reqFields = ['name', 'street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']
        validFieldsFlag = True

        _logger.info("**** reqFields: " + str(reqFields))
        for partner in partners:
            _logger.info("**** ITERA EL PARTNER: " + str(partner.id))
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                _logger.info("**** EVALUANDO EL CAMPO: " + str(reqField))
                _logger.info("**** partner[reqField]" + str(partner[reqField]))
                if not partner[reqField]:
                    _logger.info("**** NO SE ENCONTRÓ EL CAMPO")
                    validFieldsFlag = False

                _logger.info("**** validFieldsFlag: " + str(validFieldsFlag))
                
            if validFieldsFlag:
                _logger.info("**** ACTUALIZA EL CLIENTE CON CUSTOMER_TYPE A")
                self.env['res.partner'].write({'customer_type': 'A'})

            if partner['establishment_status'] == 'C':
                raise UserError("No se puede crear un pedido para un establecimiento cerrado.")

        _logger.info("**** FINALIZA _validateMainPartnerData")
        return validFieldsFlag


    def _validateAddrPartnerData(self, partners):
        _logger.info("**** INICIA _validateAddrPartnerData")
        # Campos requeridos en el cliente para continuar con el pedido
        reqFields = ['street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']

        validFieldsFlag = True

        _logger.info("**** reqFields: " + str(reqFields))
        for partner in partners:
            _logger.info("**** ITERA EL PARTNER: " + str(partner.id))
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                _logger.info("**** EVALUANDO EL CAMPO: " + str(reqField))
                _logger.info("**** partner[reqField]" + str(partner[reqField]))
                if not partner[reqField]:
                    _logger.info("**** NO SE ENCONTRÓ EL CAMPO")
                    validFieldsFlag = False

                _logger.info("**** validFieldsFlag: " + str(validFieldsFlag))

            # No lo actualiza porque estas son solo direcciones  
            #if validFieldsFlag:
            #    _logger.info("**** ACTUALIZA EL CLIENTE CON CUSTOMER_TYPE A")
            #    self.env['res.partner'].write({'customer_type', 'A'})

        _logger.info("**** FINALIZA _validateAddrPartnerData")
        return validFieldsFlag
            
    def _validateInvoicePartnerData(self, partners):
        _logger.info("**** INICIA _validateInvoicePartnerData")
        # Campos requeridos en el cliente para continuar con el pedido
        reqFields = ['vat', 'forma_pago', 'methodo_pago', 'uso_cfdi', 'street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']

        validFieldsFlag = True

        _logger.info("**** reqFields: " + str(reqFields))
        for partner in partners:
            _logger.info("**** ITERA EL PARTNER: " + str(partner.id))
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                _logger.info("**** EVALUANDO EL CAMPO: " + str(reqField))
                _logger.info("**** partner[reqField]" + str(partner[reqField]))
                if not partner[reqField]:
                    _logger.info("**** NO SE ENCONTRÓ EL CAMPO")
                    validFieldsFlag = False

                _logger.info("**** validFieldsFlag: " + str(validFieldsFlag))

            if validFieldsFlag:
                _logger.info("**** ACTUALIZA EL CLIENTE CON CUSTOMER_TYPE A")
                self.env['res.partner'].write({'customer_type': 'A'})

        _logger.info("**** FINALIZA _validateInvoicePartnerData")
        return validFieldsFlag
                
    @api.model
    def create(self, vals):
        
        if 'partner_id' in vals:
            _logger.info("**** GUARDANDO partner_id ")
            partnerMain = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
            validMainPartner = self._validateMainPartnerData(partnerMain)
            if not validMainPartner:
                raise UserError("Capture todos los datos requeridos para el cliente.")
        if 'partner_invoice_id' in vals:
            _logger.info("**** GUARDANDO partner_invoice_id ")
            partnerInv = self.env['res.partner'].search([('id', '=', vals['partner_invoice_id'])])
            validInvPartner = self._validateInvoicePartnerData(partnerInv)
            if not validInvPartner:
                raise UserError("Capture todos los datos requeridos para la dirección de facturación.")
        if 'partner_shipping_id' in vals:
            _logger.info("**** GUARDANDO partner_shipping_id ")
            partnerShip = self.env['res.partner'].search([('id', '=', vals['partner_shipping_id'])])
            validShipPartner = self._validateAddrPartnerData(partnerShip)
            if not validShipPartner:
                raise UserError("Capture todos los datos requeridos para la dirección de entrega.")

        # Si todo sale bien guarda el pedido
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        for order in self:
            if 'partner_invoice_id' in vals:
                partnerInv = self.env['res.partner'].search([('id', '=', vals['partner_invoice_id'])])
                validInvPartner = self._validateAddrPartnerData(partnerInv)

                if not validInvPartner:
                    raise UserError("Capture todos los datos requeridos para la dirección de facturación.")
            
            if 'partner_shipping_id' in vals:
                partnerShip = self.env['res.partner'].search([('id', '=', vals['partner_shipping_id'])])
                validShipPartner = self._validateAddrPartnerData(partnerShip)

                if not validShipPartner:
                    raise UserError("Capture todos los datos requeridos para la dirección de entrega.")

            if 'partner_id' in vals:
                partnerMain = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
                validMainPartner = self._validateMainPartnerData(partnerMain)

                if not validMainPartner:
                    raise UserError("Capture todos los datos requeridos para el cliente.")
            

        return super(SaleOrder, self).write(vals)
        
    # Para ejecutar la devolución automática de los productos.
    def action_cancel(self):
        _logger.info('**** Entra a action_cancel: ')
        res = super(SaleOrder, self).action_cancel()
        last_movement = self.env['stock.picking'].search([('sale_id', '=', self.id)], limit = 1, order='date_done desc')
        # Si el ultimo movimiento corresponde a una orden de entrega de ese almacén
        if last_movement.picking_type_id == last_movement.picking_type_id.warehouse_id.out_type_id and last_movement.state == 'done':
            last_movement.action_reverse_automatic()
        return res