import logging
from odoo import models, fields, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)
class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    ieps_section = fields.Boolean(default = False, help = 'Check if this group should be shown as IEPS on sales reports', string='IEPS seciton on reports.')
    iva_section = fields.Boolean(default = False, help = 'Check if this group should be shown as IVA on sales reports', string='IVA seciton on reports.')