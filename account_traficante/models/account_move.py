
from odoo import models, fields, api, SUPERUSER_ID


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_file = fields.Binary(string='Invoice document')

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        return super(AccountMove, self.sudo()).message_post(**kwargs)