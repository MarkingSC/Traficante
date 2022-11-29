from datetime import date
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
class productTemplate(models.Model):
    _name = 'product.active.history'
    _description = 'Product active history'

    product_id = fields.Many2one('product.template', string='Product', required=True)
    date = fields.Datetime(string='Date', required=True,
                       default=fields.Datetime.now)
    active_state = fields.Boolean(string='Active state')
    user_id = fields.Many2one(string='Responsible', help='User who made this change', comodel_name='res.users')
