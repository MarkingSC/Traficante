# -*- coding: utf-8 -*-
{
    'name': "Traficante's accounting and payments report",

    'summary': """
        Creates report for accounting and payments report""",

    'description': """
        - Adds account_payments_report model
        - Adds a report wizard
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'base_accounting_kit', 'report_xlsx', 'traficante_sales_detailed_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_view.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
