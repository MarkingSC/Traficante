# -*- coding: utf-8 -*-

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_type = fields.Selection([
        ('composicion', 'Composición'),
        ('descomposicion', 'Descomposición'),
    ], string='Tipo de orden', required=True, default='composicion')
