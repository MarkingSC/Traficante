# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de CRM para Traficante",

    'summary': """
        Confirugaciones y adaptaciones para la adaptación de procesos de CRM de Traficante""",

    'description': """
        - Creación de etapas de CRM de traficante.
        - Creación de registros de fuentes de oportunidades.
    """,

    'author': "Marco Martinez",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'crm',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'traficante_settings'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'data/utm_source_data.xml',
        'data/crm_team_data.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
