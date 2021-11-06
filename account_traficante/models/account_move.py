
from odoo import models, fields, api, SUPERUSER_ID


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_file = fields.Binary(string='Invoice document')
    partner_business_name = fields.Char(string='Razón social')

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        return super(AccountMove, self.sudo()).message_post(**kwargs)

    @api.onchange('partner_id')
    def _update_business_name(self):
        self.partner_business_name = self.partner_id.business_name