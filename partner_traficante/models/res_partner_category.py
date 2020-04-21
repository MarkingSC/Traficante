
from odoo import models, fields


class ResPartnerCategory(models.Model):
    _name = 'res.partner.category'
    _description = 'Partner category'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
