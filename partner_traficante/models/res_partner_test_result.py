
from odoo import models, fields


class ResPartnerTestResult(models.Model):

    _name = 'res.partner.test.result'
    _description = "Results for Partner tests"

    name = fields.Char(string = "Label")
    res_field = fields.Selection(selection = [('payment', 'Payment'),
                                              ('purchase', 'Purchases')], string  = "Field", help  = "Related test field")
    description = fields.Text(string="Description")
    sup_limit = fields.Float(string = "Superior Limit")
    inf_limit = fields.Float(string="Inferior Limit")
