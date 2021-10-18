# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de productos para Traficante",

    'summary': """
        Modifica las características de los produtos para Traficante""",

    'description': """
        - Modificación del método de obtención de cantidades en inventario.
        
    """,

    'author': "Marco Martinez",
    'website': "www.linkedin.com/in/marco-alejandro-martínez-26b68616b",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
