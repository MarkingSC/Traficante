# -*- coding: utf-8 -*-
{
    'name': "CFDI Cancellation implementations",

    'summary': """
       Add a note in a CFDI cancellation""",

    'description': """
        - Implements forms to specify a reason in a CFDI cancellation.
        - Only compatible with cdfi_ivoice module from ItAdmin
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['cdfi_invoice'],

    # always loaded
    'data': [
        'views/account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
