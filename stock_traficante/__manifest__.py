# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de Stock para Traficante",

    'summary': """
        Crea y actualiza los registros necesarios para el funcionamiento del módulo de inventario para Traficante""",

    'description': """
        - Modifica el campo 'valor' del reporte de inventario para volverlo opcional en la vista.
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_quant_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
