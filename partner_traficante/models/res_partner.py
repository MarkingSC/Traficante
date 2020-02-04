
from odoo import models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    zone_id = fields.Many2one('res.partner.zone', string='Zone')
    start_delivery_time = fields.Float(string="Start delivery time")
    finish_delivery_time = fields.Float(string="Finish delivery time")
    default_journal_id = fields.Many2one('account.journal', string='Journal', required=False, readonly=False,
                                        tracking=True,
                                        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")