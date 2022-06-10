# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

{
    'name': 'Low Stock Notification / Alert',
    'category': 'Stock',
    'version': '13.0.1.0',
    'sequence':5,
    'summary': "Apps for Product low stock alerts on product minimum stock alerts on product low stock notification on product stock alerts warehouse low stock alerts Print product Low Stock Report Minimum Stock Reminder Email Stock notify Email product stock alert,Stock Notification, Low stock, Product stock, Low Stock Report, inventory report",
    'description': "Plugin will help to notify when stock is low which define by stock manager.",
    'author': 'OM Apps',
    'website': '',
    'depends': ['sale_management','sale_stock'],
    'data': [
        'data/ir_cron_data.xml',
        'views/res_config_views.xml',
        'views/product_template_views.xml',
        'wizard/low_stock_notification_views.xml',
        'reports/report_template.xml',
        'reports/report.xml',
        'edi/mail_template_data.xml',
    ],
    'installable': True,
    'application': True,
    'images' : ['static/description/banner.png'],
    "price": 18,
    "currency": "EUR",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
