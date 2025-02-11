# -*- coding: utf-8 -*-
{
    'name': "Stock lot validations",

    'summary': """
       Validates available quantity per lot/location/product on stock moves""",

    'description': """
        - Validates available quantity per lot/location/product on stock moves
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
