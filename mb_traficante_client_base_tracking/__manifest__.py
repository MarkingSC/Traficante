# -*- coding: utf-8 -*-
{
    'name': "Módulo de seguimiento de cartera",

    'summary': """
        Permite tener un historial de los ejecutivos asignados a los clientes y agrega una columna en el detallado de ventas.""",

    'description': """
        - Modificación del formulario de clientes para agregar el historial de ejecutivos.
        - Modificación de la vista del detallado de ventas para agregar columna de seguimiento de cartera.
        
    """,

    'author': "Marco Martinez",
    'website': "www.linkedin.com/in/marco-alejandro-martínez-26b68616b",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'traficante_sales_detailed_report', 'partner_business_name'],

    # always loaded
    'data': [        
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
