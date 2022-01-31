# -*- coding: utf-8 -*-

from odoo import fields, models, api,_ 

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

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
        string=_('Forma de pago'), related = 'partner_id.forma_pago', required = True
    )
    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
				   ('PPD', _('Pago en parcialidades o diferido')),],
        string=_('Método de pago'), related = 'partner_id.methodo_pago', required = True
    )
    uso_cfdi = fields.Selection(
        selection=[('G01', _('Adquisición de mercancías')),
                   ('G02', _('Devoluciones, descuentos o bonificaciones')),
                   ('G03', _('Gastos en general')),
                   ('I01', _('Construcciones')),
                   ('I02', _('Mobiliario y equipo de oficina por inversiones')),
                   ('I03', _('Equipo de transporte')),
                   ('I04', _('Equipo de cómputo y accesorios')),
                   ('I05', _('Dados, troqueles, moldes, matrices y herramental')),
                   ('I06', _('Comunicacion telefónica')),
                   ('I07', _('Comunicación Satelital')),
                   ('I08', _('Otra maquinaria y equipo')),
                   ('D01', _('Honorarios médicos, dentales y gastos hospitalarios')),
                   ('D02', _('Gastos médicos por incapacidad o discapacidad')),
                   ('D03', _('Gastos funerales')),
                   ('D04', _('Donativos')),
                   ('D07', _('Primas por seguros de gastos médicos')),
                   ('D08', _('Gastos de transportación escolar obligatoria')),
                   ('D10', _('Pagos por servicios educativos (colegiaturas)')),
                   ('P01', _('Por definir')),],
        string=_('Uso CFDI (cliente)'), related = 'partner_id.uso_cfdi', required = True
    )


    @api.onchange("partner_id")
    def get_cfdi_data_from_partner(self):
        self.methodo_pago = self.partner_id.methodo_pago
        self.forma_pago = self.partner_id.forma_pago
        self.uso_cfdi = self.partner_id.uso_cfdi

    # 31 ENERO 2022 - Se comenta para poder probar 4.0
    # Envía de forma automática el correo de la factura cuando se timbre
    def action_cfdi_generate(self):
        _logger.info('**** entra a action_cfdi_generate: ')
        result = super(AccountMove, self).action_cfdi_generate()
        if result == True:
            _logger.info('**** Se generó el CFDI y se enviará por correo. ')
            #self.force_invoice_send()
            _logger.info('**** Factura enviada. ')
        return result

    # Envía de forma automática el correo de la Nota de crédito cuando se timbre
    def action_cfdi_cancel(self):
        _logger.info('***** entra a action_cfdi_cancel *****')
        result = super(AccountMove, self).action_cfdi_cancel()
        #_logger.info('**** Se generó la nota de credito y se enviará por correo. ')
        #self.force_invoice_send() en realidad la cancelación del cfdi no es como tal la creacion de la nota de crédito
        #_logger.info('**** Nota de crédito enviada. ')

    @api.model
    def _reverse_move_vals(self,default_values, cancel=True):
    # Cuando se crea una nota de crédito la crea desde 0 para que se pueda timbrar
        values = super(AccountMove, self)._reverse_move_vals(default_values, cancel)
        if self.estado_factura == 'factura_correcta':
            values['estado_factura'] = 'factura_no_generada'
            values['folio_fiscal'] = ''
            values['fecha_factura'] = None
            values['factura_cfdi'] = False
        return values