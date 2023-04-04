
import logging
from datetime import  datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):
    _inherit = 'sale.order'
      
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
        string=_('Forma de pago'), compute='_get_def_cfdi_data'
    )
    #num_cta_pago = fields.Char(string=_('Núm. Cta. Pago'))
    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
                   ('PPD', _('Pago en parcialidades o diferido')),],
        string=_('Método de pago'), compute='_get_def_cfdi_data'
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
                   ('S01', _('Sin efectos fiscales')),
                   ('P01', _('Por definir')),],
        string=_('Uso CFDI (cliente)'), compute='_get_def_cfdi_data'
    )

    '''
    @api.onchange("partner_invoice_id")
    def get_cfdi_data_from_partner(self):
        _logger.info('*** get_cfdi_data_from_partner ***')
        self.methodo_pago = self.partner_invoice_id.methodo_pago
        self.forma_pago = self.partner_invoice_id.forma_pago
        self.uso_cfdi = self.partner_invoice_id.uso_cfdi

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        _logger.info('*** onchange_partner_id ***')
        super(SaleOrder, self).onchange_partner_id()
        self.methodo_pago = self.partner_invoice_id.methodo_pago
        self.forma_pago = self.partner_invoice_id.forma_pago
        self.uso_cfdi = self.partner_invoice_id.uso_cfdi

    '''
    
    api.depends('partner_invoice_id')
    def _get_def_cfdi_data(self):
        _logger.info('*** _get_def_cfdi_data ***')
        self.methodo_pago = self.partner_invoice_id.methodo_pago
        self.forma_pago = self.partner_invoice_id.forma_pago
        self.uso_cfdi = self.partner_invoice_id.uso_cfdi
    

    def write(self, vals):
        _logger.info('*** write ')
        if 'partner_invoice_id' in vals:
            partner_invoice_id = self.env['res.partner'].search([('id', '=', vals['partner_invoice_id'])])
            vals['methodo_pago'] = partner_invoice_id.methodo_pago
            vals['forma_pago'] = partner_invoice_id.forma_pago
            vals['uso_cfdi'] = partner_invoice_id.uso_cfdi    

        res = super(SaleOrder, self).write(vals)
        return res
