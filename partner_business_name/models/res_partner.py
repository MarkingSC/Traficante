
from odoo import models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    business_name = fields.Char(string='Business name')
