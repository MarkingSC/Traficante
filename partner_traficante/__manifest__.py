# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de contactos para Traficante",

    'summary': """
        Modifica los modelos necesarios para la adaptación al proceso de Traficante""",

    'description': """
        - Creación del modelo zona para asociarlas a los contactos.
        - Modificación del modelo de contactos para agregar Zona, Horarios de entrega y resultados de clasificación.
        - Adición de vistas de resolución de test de clasificación.
        - Adición de paneles de gestión de preguntas y resultados de tests.
        - Adición de funcionamiento de clasificación de clientes a partir de tests
        
    """,

    'author': "Marco Martinez",
    'website': "www.linkedin.com/in/marco-alejandro-martínez-26b68616b",

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
        'views/res_partner_test_question_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
