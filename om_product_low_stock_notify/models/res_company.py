# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

from odoo import api, models, fields, _
from odoo.osv import expression


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    is_law_stock_notification = fields.Boolean('Low Stock Notification?')
    
    low_stock_notify_on = fields.Selection([('on_hand_qty','On Hand Quantity'),('forecast','Forecast')], 
                                    string='Notification Based on', 
                                    default='on_hand_qty')
    
    min_qty_based_on = fields.Selection([('global','Global'),
                                         ('individual','Individual'),
                                         ('record_rule','Record Rules')], default='global', string='Min Quantity Based on')
                                         
    min_qty = fields.Float('Quantity Limit', default=10)
    notify_to = fields.Many2many('res.users', string='Notify To')
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouse')
    location_ids = fields.Many2many('stock.location', string='Location')
    
    def product_low_stock_notification(self):
        company_ids= self.env['res.company'].search([('is_law_stock_notification','=',True)])
        for company in company_ids:
            vals={'low_stock_notify_on':company.low_stock_notify_on,
                  'min_qty_based_on':company.min_qty_based_on,
                  'min_qty':company.min_qty,
                  'notify_to':[(6,0, company.notify_to.ids)],
                  'warehouse_ids':[(6,0, company.warehouse_ids.ids)],
                  'location_ids':[(6,0, company.location_ids.ids)],
                  'company_id':company.id}
                  
            wiz_id = self.env['low.stock.notification'].create(vals)
            if wiz_id:
                product_lst = wiz_id.get_details()
                if product_lst:
                    wiz_id.send_low_stock()
        return True
        
    
    
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    is_law_stock_notification = fields.Boolean(related='company_id.is_law_stock_notification', 
                                               string='Low Stock Notification?', readonly=False)
    low_stock_notify_on = fields.Selection(related='company_id.low_stock_notify_on', string="Notification Based on", readonly=False)
    min_qty_based_on = fields.Selection(related='company_id.min_qty_based_on', 
                                        string='Min Quantity Based on', readonly=False)
    min_qty = fields.Float(related='company_id.min_qty', string='Quantity Limit', readonly=False)
    
    notify_to = fields.Many2many('res.users',related='company_id.notify_to', string='Notify To', readonly=False)
    warehouse_ids = fields.Many2many('stock.warehouse',related='company_id.warehouse_ids', string='Warehouse', readonly=False)
    location_ids = fields.Many2many('stock.location', related='company_id.location_ids', string='Location', readonly=False)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
