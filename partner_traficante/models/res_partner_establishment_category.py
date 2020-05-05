
from odoo import models, fields


class ResPartnerEstablishmentCategory(models.Model):
    _name = 'res.partner.establishment.category'
    _description = 'Partner establishment category'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
