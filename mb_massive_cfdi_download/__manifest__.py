# -*- coding: utf-8 -*-
{
    'name': "CFDI Massive downloads",

    'summary': """
       Download all xml and PDF files generated from CFDI""",

    'description': """
        Provides users a report to download all xml and PDF files generated from CFDI
    """,

    'author': "Marco Martinez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['cdfi_invoice', 'attachment_zipped_download'],

    # always loaded
    'data': [
        'views/ir_attachment_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
