# -*- coding: utf-8 -*-

from odoo import models, fields


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    justification = fields.Char(
        string='Justificación', size=500, required=True, store=True)
