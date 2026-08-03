# -*- coding: utf-8 -*-
{
    'name': "Configuraciones de Fabricación para Traficante",

    'summary': """
        Agrega el tipo de orden (Composición / Descomposición) a las órdenes de producción""",

    'description': """
        - Agrega el campo requerido 'Tipo de orden' (Composición / Descomposición) a las órdenes de producción.
        - Muestra el campo en la vista de lista de órdenes de producción.
        - Agrega filtros de búsqueda para Composición (por defecto) y Descomposición.
    """,

    'author': "Marco Martinez",
    'website': "",

    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        'views/mrp_production_views.xml',
    ],
}
