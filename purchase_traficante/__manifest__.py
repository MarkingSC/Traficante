# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de compras para Traficante",

    'summary': """
        Configuraciones de compras para Traficante""",

    'description': """
        Modificación de vistas para compras para Traficante
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        'views/purchase_order_line_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
