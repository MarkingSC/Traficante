# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de contactos para Traficante",

    'summary': """
        Modifica los modelos necesarios para la adaptación al proceso de Traficante""",

    'description': """
        - Creación del modelo zona para asociarlas a los contactos.
        - Modificación del modelo de contactos para agregar Zona, y Horarios de entrega
    """,

    'author': "Marco Martinez",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'partner_business_name', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/account_journal_data.xml',
        'views/res_partner_views.xml',
        'views/res_partner_zone_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
