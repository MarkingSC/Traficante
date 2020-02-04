
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_file = fields.Binary(string='Invoice document')
