# -*- coding: utf-8 -*-
{
    'name': "Multi Discount for Traficante",

    'summary': """
       Provides multi discount features for Traficante""",

    'description': """
        - Changes shown discount in invoice format
        - Adds multi-discount column in sales detailed report
        - Adds multi-discount column in invoicing report
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_traficante', 'dev_multi_discount'],

    # always loaded
    'data': [
        'views/account_move_views.xml',
        'views/move_line_views.xml',
        'report/invoice_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
