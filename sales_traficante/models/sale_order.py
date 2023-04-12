
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _validateMainPartnerData(self, partners):
        reqFields = ['name', 'street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']
        validFieldsFlag = True

        for partner in partners:
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                if not partner[reqField]:
                    validFieldsFlag = False

                
            if validFieldsFlag:
                self.env['res.partner'].write({'customer_type': 'A'})

            if partner['establishment_status'] == 'C':
                raise UserError("No se puede crear un pedido para un establecimiento cerrado.")

        return validFieldsFlag


    def _validateAddrPartnerData(self, partners):
        # Campos requeridos en el cliente para continuar con el pedido
        reqFields = ['street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email']

        validFieldsFlag = True

        for partner in partners:
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                if not partner[reqField]:
                    validFieldsFlag = False

        return validFieldsFlag
            
    def _validateInvoicePartnerData(self, partners):
        # Campos requeridos en el cliente para continuar con el pedido
        reqFields = ['vat', 'forma_pago', 'methodo_pago', 'uso_cfdi', 'street2', 'city', 'state_id', 'zip', 'country_id', 'mobile', 'email', 'regimen_fiscal']

        validFieldsFlag = True

        for partner in partners:
            # Revisa si cuenta con todos los campos requeridos
            for reqField in reqFields:
                if not partner[reqField]:
                    validFieldsFlag = False


            if validFieldsFlag:
                self.env['res.partner'].write({'customer_type': 'A'})

        return validFieldsFlag
                
    @api.model
    def create(self, vals):
        
        if 'partner_id' in vals:
            partnerMain = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
            validMainPartner = self._validateMainPartnerData(partnerMain)
            if not validMainPartner:
                raise UserError("Capture todos los datos requeridos para el cliente.")
        if 'partner_invoice_id' in vals:
            partnerInv = self.env['res.partner'].search([('id', '=', vals['partner_invoice_id'])])
            validInvPartner = self._validateInvoicePartnerData(partnerInv)
            if not validInvPartner:
                raise UserError("Capture todos los datos requeridos para la dirección de facturación.")
        if 'partner_shipping_id' in vals:
            partnerShip = self.env['res.partner'].search([('id', '=', vals['partner_shipping_id'])])
            validShipPartner = self._validateAddrPartnerData(partnerShip)
            if not validShipPartner:
                raise UserError("Capture todos los datos requeridos para la dirección de entrega.")

        # Si todo sale bien guarda el pedido
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        _logger.info('*** Entra a write de sale order ***')
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
            
            # Se agrega validación para no poner el pedido 'por facturar' si tiene facturas asociadas
            if 'invoice_status' in vals:
                _logger.info('*** order.invoice_status: ' + str(order.invoice_status))
                _logger.info('*** vals[invoice_status]: ' + str(vals['invoice_status']))
                invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.type in ('out_invoice', 'out_refund'))
                if vals['invoice_status'] == 'to_invoice' and len(invoices) > 0:
                    vals['invoice_status'] == order.invoice_status             
            

        return super(SaleOrder, self).write(vals)

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoice_status(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.
        """
        
        _logger.info("*** entra a _get_invoice_status ***")

        unconfirmed_orders = self.filtered(lambda so: so.state not in ['sale', 'done'])
        unconfirmed_orders.invoice_status = 'no'
        confirmed_orders = self - unconfirmed_orders
        if not confirmed_orders:
            return
        line_invoice_status_all = [
            (d['order_id'][0], d['invoice_status'])
            for d in self.env['sale.order.line'].read_group([
                    ('order_id', 'in', confirmed_orders.ids),
                    ('is_downpayment', '=', False),
                    ('display_type', '=', False),
                ],
                ['order_id', 'invoice_status'],
                ['order_id', 'invoice_status'], lazy=False)]
        for order in confirmed_orders:
            _logger.info("*** order.invoice_status: " + str(order.invoice_status))

            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]
            _logger.info("*** order.state: " + str(order.state))
            _logger.info("*** order.invoice_count: " + str(order.invoice_count))

            # Debe estar a facturar cuando el pedido esté confirmado y no haya facturas

            if order.state not in ('sale', 'done'):
                order.invoice_status = 'no'
            #elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
            elif order.invoice_count == 0 and order.state == 'sale':
                order.invoice_status = 'to invoice'
            elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                order.invoice_status = 'invoiced'
            elif line_invoice_status and all(invoice_status in ('invoiced', 'upselling') for invoice_status in line_invoice_status):
                order.invoice_status = 'upselling'
            else:
                order.invoice_status = 'no'

            _logger.info("*** order.invoice_status: " + str(order.invoice_status))

    # Para ejecutar la devolución automática de los productos.
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        last_movement = self.env['stock.picking'].search([('sale_id', '=', self.id)], limit = 1, order='date_done desc')
        # Si el ultimo movimiento corresponde a una orden de entrega de ese almacén
        if last_movement.picking_type_id == last_movement.picking_type_id.warehouse_id.out_type_id and last_movement.state == 'done':
            last_movement.action_reverse_automatic()
        return res


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'