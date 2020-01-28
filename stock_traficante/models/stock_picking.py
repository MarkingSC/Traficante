
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def get_invoices(self):
        self.invoice_ids = self.env['account.move'].search([('invoice_origin', '=', self.origin)]).ids
        _logger.debug('//////////////')
        _logger.debug(self.invoice_ids)

    invoice_ids = fields.Many2many('account.move', ondelete='restrict', string='invoices', compute=get_invoices)

