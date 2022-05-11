import logging
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    reinvoice = fields.Boolean(string = 'Extemporaneous reinvoice', help="Check if this invoice is defined as extemporaneups reinvoicing.")