
import logging
from odoo import models, fields, api, _, exceptions
from datetime import timedelta, datetime

datetime.today()

_logger = logging.getLogger(__name__)

class stockQuant(models.Model):
    _inherit = 'stock.quant'

    product_category = fields.Many2one(
        'product.category', 'Category', store=True,
        readonly=True, related='product_id.categ_id')

    warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse', store=True, compute='_get_quant_warehouse_id')

    @api.depends('location_id')
    def _get_quant_warehouse_id(self):
        for quant in self:
            location = quant.location_id
            if location:
                warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', location.id)], limit=1)
                quant.warehouse_id = warehouse.id if warehouse else False