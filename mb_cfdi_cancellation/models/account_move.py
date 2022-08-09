import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = 'account.move'

    internal_cancel_reason = fields.Text(string='Cancellation reason',help="Specify a reason why this invoice is being cancelled. This is for internal use.")


class ReasonCancelation(models.TransientModel):
    _inherit ='reason.cancelation'

    internal_cancel_reason = fields.Text(string='Cancellation reason',help="Specify a reason why this invoice is being cancelled. This is for internal use.", required=True)

    def Confirmar(self):
        if self.env.context.get('active_id') and self.env.context.get('active_model') == "account.move":
            move_obj = self.env['account.move'].browse(self.env.context['active_id'])
            print(move_obj)
            ctx = {'motivo_cancelacion':self.motivo_cancelacion,'foliosustitucion':self.foliosustitucion or False}
            res = move_obj.with_context(ctx).action_cfdi_cancel()
            move_obj.write({'internal_cancel_reason':self.internal_cancel_reason})
            return res
        if self.env.context.get('active_id') and self.env.context.get('active_model') == "account.payment":
            move_obj = self.env['account.payment'].browse(self.env.context['active_id'])
            print(move_obj)
            ctx = {'motivo_cancelacion':self.motivo_cancelacion,'foliosustitucion':self.foliosustitucion or False}
            res = move_obj.with_context(ctx).action_cfdi_cancel()
            move_obj.write({'internal_cancel_reason':self.internal_cancel_reason})
            return res
        if self.env.context.get('active_id') and self.env.context.get('active_model') == "cfdi.traslado":
            move_obj = self.env['cfdi.traslado'].browse(self.env.context['active_id'])
            print(move_obj)
            ctx = {'motivo_cancelacion':self.motivo_cancelacion,'foliosustitucion':self.foliosustitucion or False}
            res = move_obj.with_context(ctx).action_cfdi_cancel()
            move_obj.write({'internal_cancel_reason':self.internal_cancel_reason})
            return res
        if self.env.context.get('active_id') and self.env.context.get('active_model') == "factura.global":
            move_obj = self.env['factura.global'].browse(self.env.context['active_id'])
            print(move_obj)
            ctx = {'motivo_cancelacion':self.motivo_cancelacion,'foliosustitucion':self.foliosustitucion or False}
            res = move_obj.with_context(ctx).action_cfdi_cancel()
            move_obj.write({'internal_cancel_reason':self.internal_cancel_reason})
            return res
