
import logging
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class AccountMove(models.Model):

    _inherit = 'account.move'

    def post(self):
        res =  super(AccountMove, self).post()
        # update_amount_on_post_move
        for move in self:
            last_date = self._get_date_from_invoice(move)
            if last_date:
                self.env['account.invoice.avg']._update_amount(last_date, move.partner_id)
        return  res

    @api.model
    def _get_date_from_invoice(self, move):
        if (move.type == 'out_invoice' or move.type == 'out_refund'):
            if move.type == 'out_invoice':
                return move.invoice_date
            elif move.type == 'out_refund':
                return move.reversed_entry_id.invoice_date
