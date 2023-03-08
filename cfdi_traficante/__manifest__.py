# -*- coding: utf-8 -*-
{
    'name': "Configuraciones del modulo de timbrado con CFDI para Traficante",

    'summary': """
        Modifica los modelos necesarios para la adaptación al proceso de emisión de facturas de Traficante""",

    'description': """
        - Adicion de campos de uso, forma de pago y método de pago al formulario de contactos
        - Inhabilita los campos de uso, forma de pago y método de pago en el formulario de facturas y pedidos
        
    """,

    'author': "Marco Martinez",
    'website': "www.linkedin.com/in/marco-alejandro-martínez-26b68616b",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'partner_traficante', 'cdfi_invoice', 'currency_rate_update'],

    # always loaded
    'data': [
        'views/res_partner_views.xml',
        'views/account_payment_views.xml',
        'report/invoice_report_custom.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
