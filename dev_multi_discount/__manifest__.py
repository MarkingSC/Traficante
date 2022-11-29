# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Multiple Discount in Sale, Purchase, Invoice',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Sales Management',
    'description':
        """
        odoo module will help to give multiple discount on sale,purchase and account invoice
        
        multiple discount on sale
        multiple discount on purchase
        multiple discount on invoice
        odoo multiple discount on sale
        odoo multiple discount on purchase
        odoo multiple discount on invoice
        odoo multiple discount
        multiple discount in odoo
        multiple discount in purchase odoo
        odoo multi discount
Multiple Discount in Sale, Purchase, Invoice
Odoo Multiple Discount in Sale, Purchase, Invoice
Multiple discount in sale 
Odoo multiple discount in sale 
Multiple discount in purchase 
Odoo multiple discount in purchase 
Multiple discount in Invoice 
Odoo multiple discount in invoice 
Manage multiple discount 
Odoo manage multiple discount 
Manage discount in sale 
Odoo manage discount in sale 
Manage discount in purchase 
Odoo manage discount in purchase 
Manage discount in invoice 
Odoo manage discount in Invoice 
    """,
    'summary': 'odoo App add option for multiple discount on sale,purchase and invoice screen',
    'depends': ['sale_management','purchase','account'],
    'data': [
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/purchase_order_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':25.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
