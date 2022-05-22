# -*- coding: utf-8 -*-
{
    'name': "Traficante's stock margin report",

    'summary': """
        Modifies objects to set values and get Traficante's inventory report""",

    'description': """
        - Adds columns for res.product model.
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'account', 'traficante_sales_detailed_report', 'purchase'],

    # always loaded
    'data': [
        'data/ir_cron_data.xml',
        'wizard/report_view.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
