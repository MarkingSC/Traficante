import logging
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    photo_validation_1 = fields.Binary(string="Evidence 1 (Invoice)", readonly=False)
    photo_validation_2 = fields.Binary(string="Evidence 2 (Products)", readonly=False)

    def button_validate_with_pics(self):
        _logger.info("**** INICIA button_validate_with_pics")
        _logger.info("**** self.id: " + str(self.id))
        
        postedInvoices = self.invoice_ids.filtered(lambda r: r.estado_factura == 'factura_correcta')

        if self.picking_type_code == 'outgoing' and self.env['sale.order'].search([('name' , '=', self.origin)]):
            if len(postedInvoices)  == 0:
                raise UserError("No es posible validar el movimiento. No existen facturas timbradas para este pedido.")

            if self.on_delivery_route != True:
                raise UserError("No es posible validar el movimiento. Esta entrega debe estar programada en ruta para continuar.")

        ctx = dict(self.env.context, default_id = self.id)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Evidence uploading'),
            'res_model': 'stock.picking',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('mb_stock_photo_validation.stock_photo_validation_wizard').id,
            'target': 'new'
        }
    
    def button_validate(self):
        _logger.info("**** INICIA button_validate con self.id: " + str(self.id))

        res = super(StockPicking, self).button_validate()
        
        _logger.info('**** TERMINA button_validate *****')
        
        return res