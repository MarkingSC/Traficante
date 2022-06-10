# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

from odoo import api, models, fields, _
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    minimum_quantity = fields.Float(string='Minimum Quantity', default=10.0)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
