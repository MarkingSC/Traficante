
import logging
from odoo import models, fields, api, _, exceptions
import odoo
from datetime import timedelta, datetime
import pytz
from odoo.exceptions import AccessError, UserError, ValidationError

datetime.today()

_logger = logging.getLogger(__name__)

class CancelWizard(models.TransientModel):
    _name = 'cancel.invoice.wizard'

    yes_no = fields.Char(default='¿En caso de que existan pedidos asociados a esta factura, desea cancelar las operaciones de inventario y/o realizar la devolución de los productos?')
    invoice_id = fields.Many2one(string="Invoice", comodel_name='account.move', readonly=True)
    cancellation_reason = fields.Char(string="Motivo de cancelación", help="Especifique el motivo por el cual cancela esta factura.", required=True)

    def yes(self):
        _logger.info('**** Dijo que si')
        self.invoice_id.cancel_with_movements(self.cancellation_reason)

    def no(self):
        _logger.info('**** Dijo que no')
        self.invoice_id.cancel_invoice_only(self.cancellation_reason)

class AccountMove(models.Model):
    _inherit = 'account.move'

    cancellation_reason = fields.Char(string="Motivo de cancelación", help="Especifique el motivo por el cual cancela esta factura.")
    cancellation_date = fields.Date(string='Fecha de cancelación', help="Fecha en que se ha cancelado la factura.")
    
    # lanza el wizard para confirmación    
    def return_confirmation(self):
        _logger.info('**** entra a return_confirmation: ')
        
    
    def button_cancel_traficante(self):
        _logger.info('**** Entra a button_cancel_traficante: ')
        _logger.info('**** Sí tiene un pedido asociado, debería preguntar ')
        return {
            'name': 'Devolución de productos',
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.invoice.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id
                },
        }



    def cancel_with_movements(self, cancellation_reason):
        _logger.info('**** Sí, devolver productos.: ')
        self.cancellation_reason = cancellation_reason
        self.cancellation_date = datetime.now()
        pedido_asociado = self.env['sale.order'].search([('name', '=', self.invoice_origin)], limit = 1)
        pedido_asociado.action_cancel()
        self.button_cancel()
        
    def cancel_invoice_only(self, cancellation_reason):        
        _logger.info('**** No, solo cancelar la factura.: ')
        _logger.info('**** self: ' + str(self))
        self.cancellation_reason = cancellation_reason
        self.cancellation_date = datetime.now()
        self.button_cancel()
        

    
    