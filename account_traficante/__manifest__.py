# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de contabilidad para Traficante",

    'summary': """
    Configuraciones y adecuaciones de contabilidad para Traficante""",

    'description': """
        - Creaación de elementos de plazos de pago
    """,

    'author': "Marco Martinez",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/account_payment_term_data.xml',
        'data/account_tax_data.xml',
        'views/account_move_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
