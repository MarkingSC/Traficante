# -*- coding: utf-8 -*-
{
    'name': "Traficante's sales detailed report",

    'summary': """
        Creates objects and reports for detailed report for sales""",

    'description': """
        - Adds sales_detailed_report model
        - Adds detailed report tree view
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
        'security/ir.model.access.csv',
        'views/move_line_views.xml',
        'wizard/report_view.xml',
        'report/report.xml',
        'data/ir_cron_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
