
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Marco 23/01/2023
    invoice_date = fields.Date(string="Invoice date", compute="_get_invoice_data", store=False)

    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayment, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec

        invoices = self.env['account.move'].browse(active_ids).filtered(
            lambda move: move.is_invoice(include_receipts=True))

        journal_id = invoices[0].partner_id.default_journal_id.id
        rec.update({
            'journal_id': journal_id,
        })
        return rec

    # Marco 23/01/2023
    @api.depends('invoice_ids')
    def _get_invoice_data(self):
        for payment in self:
            first_invoice = payment.invoice_ids.search([('state', '=', 'posted'), ('id', 'in', payment.invoice_ids.ids)], limit = 1, order='date asc')
            payment.invoice_date = first_invoice.date
