
import logging
from odoo import models, fields, api, _, exceptions
from datetime import timedelta, datetime

datetime.today()

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.quant'

    product_category = fields.Many2one(
        'product.category', 'Category', store=True,
        readonly=True, related='product_id.categ_id')
