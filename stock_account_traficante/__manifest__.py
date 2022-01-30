# -*- coding: utf-8 -*-
{
    'name': "Devolución en facturas canceladas",

    'summary': """
        Implementa los procesos de devolución de productos desde la cancelación de facturas""",

    'description': """
        - Modifica los procedimientos de cancelación en facturas para lanzar una confirmación para devolver los productos relacionados.
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account', 'purchase', 'cfdi_traficante'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        #'report/stock_reports.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
