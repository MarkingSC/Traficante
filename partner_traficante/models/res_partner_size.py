
from odoo import models, fields


class ResPartnerSize(models.Model):

    _name = 'res.partner.size'
    _description = "Partner's establishment size"

    name = 'Label'
    category_id = fields.Many2one('res.partner.category',  string = "Category", help = "Category which this record belongs to")
    sup_limit = fields.Integer(string = "Superior limit")
    inf_limit = fields.Integer(string = "Inferior limit")
