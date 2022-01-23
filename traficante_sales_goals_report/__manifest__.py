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
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/uom_uom_data.xml',
        'views/stock_quant_views.xml',
        'report/stock_reports.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
