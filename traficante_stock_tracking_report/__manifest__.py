# -*- coding: utf-8 -*-
{
    'name': "Traficante's stock tracking report for lot numbers",

    'summary': """
        Allow user to get a tracking report based on lot number of products""",

    'description': """
        - Modifies 
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'account', 'traficante_stock_report'],

    # always loaded
    'data': [
        'views/stock_move_line_views.xml',
        'views/stock_move_view.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/report_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
