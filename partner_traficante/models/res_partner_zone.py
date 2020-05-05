
from odoo import models, fields


class ResPartnerZone(models.Model):

    _name = 'res.partner.zone'

    name = fields.Char(string='Name of zone', required = True)
    description = fields.Char(string='Description of the Zone', required = True)