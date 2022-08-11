
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class ResPartner(models.Model):

    _inherit = 'res.partner'

    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
                   ('PPD', _('Pago en parcialidades o diferido')),],
        string=_('Método de pago'), 
    )

    forma_pago = fields.Selection(
        selection=[('01', '01 - Efectivo'), 
                   ('02', '02 - Cheque nominativo'), 
                   ('03', '03 - Transferencia electrónica de fondos'),
                   ('04', '04 - Tarjeta de Crédito'), 
                   ('05', '05 - Monedero electrónico'),
                   ('06', '06 - Dinero electrónico'), 
                   ('08', '08 - Vales de despensa'), 
                   ('12', '12 - Dación en pago'), 
                   ('13', '13 - Pago por subrogación'), 
                   ('14', '14 - Pago por consignación'), 
                   ('15', '15 - Condonación'), 
                   ('17', '17 - Compensación'), 
                   ('23', '23 - Novación'), 
                   ('24', '24 - Confusión'), 
                   ('25', '25 - Remisión de deuda'), 
                   ('26', '26 - Prescripción o caducidad'), 
                   ('27', '27 - A satisfacción del acreedor'), 
                   ('28', '28 - Tarjeta de débito'), 
                   ('29', '29 - Tarjeta de servicios'),
                   ('30', '30 - Aplicación de anticipos'),
                   ('99', '99 - Por definir'),],
        string=_('Forma de pago'),
    )

    def _get_current_forma_pago(self):
        res = []
        for record in self:
            res.append((record.id, record.forma_pago))
        return res

    forma_pago_pue = fields.Selection(
        selection=[('01', '01 - Efectivo'), 
                   ('02', '02 - Cheque nominativo'), 
                   ('03', '03 - Transferencia electrónica de fondos'),
                   ('04', '04 - Tarjeta de Crédito'), 
                   ('28', '28 - Tarjeta de débito')],
        string=_('Forma de pago'), 
        default = _get_current_forma_pago
    )

    forma_pago_ppd = fields.Selection(
        selection=[('99', '99 - Por definir')],
        string=_('Forma de pago'), 
        default = _get_current_forma_pago
    )

    @api.onchange('methodo_pago')
    def reset_forma_pago(self):
        for record in self:
            record.forma_pago_pue = False
            record.forma_pago_ppd = False

    @api.onchange('forma_pago_pue', 'forma_pago_ppd')
    def set_forma_pago(self):
        for record in self:
            _logger.info("**** Entra a set_forma_pago con record: " + str(record))
            _logger.info("**** record.forma_pago antes: " + str(record.forma_pago))
            if record.forma_pago_pue == False and record.forma_pago_ppd == False:
                record.forma_pago = False
            elif record.forma_pago_pue != False:
                record.forma_pago = record.forma_pago_pue
            elif record.forma_pago_ppd != False:
                record.forma_pago = record.forma_pago_ppd

            _logger.info("**** record.forma_pago despues: " + str(record.forma_pago))
        
    @api.model
    def create(self, vals):
        _logger.info("**** Entra a create con vals: " + str(vals))
        if 'vat' in vals and vals['vat']:
            _logger.info("**** RFC entrante " + str(vals['vat']))
            foundVat = self.env['res.partner'].search([('vat', '=', vals['vat'])])
            if len(foundVat) > 0:                
                raise UserError("Ya existe un registro con el mismo RFC.")

        record = super(ResPartner, self).create(vals)
        return record
