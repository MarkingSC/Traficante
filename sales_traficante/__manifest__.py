# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de ventas para Traficante",

    'summary': """
        Modifica los modelos necesarios para la adaptación al proceso de Traficante""",

    'description': """
        - Modificación de las funciones de creación y modificación de pedidos de venta para validar que el cliente tenga datos fiscales y de entrega
        - Implementación de la devolución automática de productos desde la cancelación de pedidos
        
    """,

    'author': "Marco Martinez",
    'website': "www.linkedin.com/in/marco-alejandro-martínez-26b68616b",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'partner_traficante', 'cfdi_traficante'],

    # always loaded
    'data': [
        'security/stock_security.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
