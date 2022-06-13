# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang

class LowStockNotification(models.TransientModel):
    _name = "low.stock.notification"
    _description = "Low Stock Notification"
    
    
    low_stock_notify_on = fields.Selection([('on_hand_qty','On Hand Quantity'),('forecast','Forecast')], 
                                    string='Notification Based on', 
                                    default='on_hand_qty')
    
    min_qty_based_on = fields.Selection([('global','Global'),
                                         ('individual','Individual'),
                                         ('record_rule','Record Rules')], default='global', string='Minimum Quantity Based On')
                                         
    min_qty = fields.Float('Minimum Quantity', default=10)
    notify_to = fields.Many2many('res.users', string='Send Nofitication')
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouse')
    location_ids = fields.Many2many('stock.location', string='Location')
    company_id = fields.Many2one('res.company', default=lambda self:self.env.user.company_id)
    
    def get_minimum_qty(self,product):
        if self.min_qty_based_on == 'global':
            return self.min_qty
        elif self.min_qty_based_on == 'individual':
            return product.minimum_quantity
        else:
            rule_id = self.env['stock.warehouse.orderpoint'].search([('product_id','=',product.id),
                                                                     ('company_id','=',self.company_id.id)], limit=1)
            if rule_id:
                return rule_id.product_min_qty
            else:
                return 0
    
    def get_details(self):
        lst=[]
        product_ids = self.env['product.product'].sudo().search([('type','=','product')])
        
        context = {}
        if self.warehouse_ids:
            context.update({'warehouse':self.warehouse_ids.ids})
        if self.location_ids:
            context.update({'location':self.location_ids.ids})
        for product in product_ids:
            min_qty = self.get_minimum_qty(product)
            if context:
                product = product.with_context(context)
            vals = product._product_available()
            on_hand_qty = 0.0
            if self.low_stock_notify_on == 'on_hand_qty':
                on_hand_qty = vals.get(product.id).get('qty_available')
            else:
                on_hand_qty = vals.get(product.id).get('virtual_available')
            if on_hand_qty <= min_qty:
                lst.append({
                    'product':product.display_name,
                    'stock':formatLang(self.env, on_hand_qty),
                    'minimum_qty':formatLang(self.env, min_qty),
                })
        return lst
        
    
    def get_email(self):
        email = ''
        if self.notify_to:
            email = ','.join(map(lambda user: (user.partner_id.email), self.notify_to))
        return email
        
    def send_low_stock(self):
        if not self.notify_to:
            raise ValidationError(_('Please Add Users in Send Notification'))
        template_id = self.env.ref('om_product_low_stock_notify.send_low_stock_notification_email')
        email = self.get_email()
        if email and template_id:
            template_id.email_to = email
            template_id.send_mail(self.id, force_send=True)
        return True
            
    
    def print_pdf_report(self):
        data= {}
        return self.env.ref('om_product_low_stock_notify.low_stock_nitification_report').report_action([], data=data)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
