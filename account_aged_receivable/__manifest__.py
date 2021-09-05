# -*- coding: utf-8 -*-
{
    'name': "Obtención de saldos vencidos de empresas",

    'summary': """
        Agrega los elementos necesarios para acceder al informe de saldos vencidos.""",

    'description': """
        Agrega los elementos necesarios para acceder al informe de saldos vencidos.
        
    """,

    'author': "Marco Martinez",
    'website': "www.linkedin.com/in/marco-alejandro-martínez-26b68616b",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
        'data/ir_actions_client_data.xml',
    ],
}
