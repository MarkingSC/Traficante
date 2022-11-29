# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class sale_order_line(models.Model):
    _inherit= 'sale.order.line'
    
    
    multi_discount = fields.Char('Multi Discount')
    discount_amt = fields.Float('Discount Amt',compute = 'get_discount_amount')
    
    
    @api.depends('discount','multi_discount','price_unit')
    def get_discount_amount(self):
        for line in self:
            line.discount_amt = 0
            if line.discount and line.price_unit:
                line.discount_amt = ( line.price_unit * line.discount ) / 100
                
    def _prepare_invoice_line(self):
        res = super(sale_order_line,self)._prepare_invoice_line()
        if self.multi_discount:
            res.update({
                'multi_discount':self.multi_discount,
            })
        return res


                
    def isfloat(self,value):
      try:
        float(value)
        return True
      except ValueError:
        return False
    
    def check_is_number(self):
        for line in self:
            discounts = line.multi_discount.split('+')
            for dis in discounts:
                is_float_num = self.isfloat(dis)
                if '.' in dis:
                    is_float_num = self.isfloat(dis)
                    if is_float_num:
                        dis = float(dis)
                    else:
                        raise ValidationError(_("You must Enter Integer or Float in Multi Discount"))
                else:
                    if dis.isdigit():
                        dis = int(dis)
                    else:
                        raise ValidationError(_("You must Enter Integer or Float in Multi Discount"))
                
            
    @api.onchange('multi_discount','price_unit')
    def onchange_multi_discount(self):
        if self.multi_discount and self.price_unit:
            self.check_is_number()
            discounts = self.multi_discount.split('+')
            amount = self.price_unit
            total_discount = 0
            for dis in discounts:
                if dis:
                    dis = float(dis)
                    dis_amount = ( amount * dis ) / 100
                    total_discount += dis_amount
                    amount = amount - dis_amount
            
            if total_discount and self.price_unit:
                discount = (total_discount * 100) / self.price_unit
                self.discount = discount
            
                
                
                
    
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
