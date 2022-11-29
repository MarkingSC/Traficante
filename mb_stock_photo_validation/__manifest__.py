# -*- coding: utf-8 -*-
{
    'name': "Stock photo validations",

    'summary': """
       Ask for pictures to validate deliveries""",

    'description': """
        - Implements validation form for deliveries
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_traficante'],

    # always loaded
    'data': [
        'views/stock_picking_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
