{
    'name': "Business name for partners",

    'summary': """
        This module allows to define a business name for contacts that are
         companies.""",

    'author': 'BerrySoft Mx, '
              'Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/partner-contact",
    'license': "AGPL-3",

    'category': 'Customer Relationship Management',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
}
