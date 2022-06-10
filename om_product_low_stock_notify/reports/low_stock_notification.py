# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

from odoo import models, fields
from odoo.tools.misc import formatLang
from datetime import datetime,date
from odoo.tools.misc import formatLang


class LowStockNotification(models.AbstractModel):
    _name = 'report.om_product_low_stock_notify.low_stock_template'

        
    def _get_report_values(self, docids, data=None):
        docs = self.env['low.stock.notification'].browse(docids)
        docargs = {
            'docs':docs,
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
