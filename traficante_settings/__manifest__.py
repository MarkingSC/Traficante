# -*- coding: utf-8 -*-
{
    'name': "Configuraciones y datos para Traficante",

    'summary': """
        Configuraciones y datos para traficante""",

    'description': """
        Crea los registros de usuarios para Traficante.
        Establece los datos de la compañía correspondientes a Traficante.
    """,

    'author': "Marco Martinez",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'crm', 'purchase', 'stock', 'contacts', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_ui_menu_views.xml',
        'data/res_users_data.xml',
        'data/res_company_data.xml',
        'security/ir_model_access_data.xml',
    ],

    'qweb': ["static/src/xml/base.xml"],
}
