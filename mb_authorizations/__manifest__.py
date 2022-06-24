# -*- coding: utf-8 -*-
{
    'name': "Authorizations",

    'summary': """
       Allows users to automatically create authorization tasks""",

    'description': """
        - Adds autohrization policies (conditions) management.
        - Adds authorization tasks management.
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'data/authorization_policy_data.xml',
        'data/mail_template_data.xml',
        'views/authorization_policy_views.xml',
        'views/authorization_task_views.xml',
        'views/ir_ui_menu_views.xml',
        'security/authorization_security.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
