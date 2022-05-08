# -*- coding: utf-8 -*-
{
    'name': "Traficante's sales goals report",

    'summary': """
        Creates objects and reports for traficante's sales goals report""",

    'description': """
        - Adds report_section model
        - Adds sales_goal model
        - Adds acces rules for report elements
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'base_accounting_kit', 'report_xlsx'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',
        'views/sales_goal_views.xml',
        'views/sales_goal_section_type_views.xml',
        'wizard/report_view.xml',
        'report/report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
