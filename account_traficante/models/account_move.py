
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_status = fields.Char(string='Delivery status')
    delivery_notes = fields.Text(string='Delivery notes')
    delivery_date = fields.Date(string='Delivery date')
    invoice_file = fields.Binary(string='Invoice document')
