
from odoo import models, fields


class ResPartnerSize(models.Model):

    _name = 'res.partner.size'
    _description = "Partner's establishment size"

    name = fields.Char(string='Label', required = True)
    est_category_id = fields.Many2one('res.partner.establishment.category',  string = "Category",
                                      help = "Category which this record belongs to", required = True)
    sup_limit = fields.Integer(string = "Superior limit", required = True)
    inf_limit = fields.Integer(string = "Inferior limit", required = True)
