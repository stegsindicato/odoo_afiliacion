# -*- coding: utf-8 -*-
{
    'name': "steg_afiliacion",

    'summary': "Este módulo engade como modelos aos Centros Educativos e aos Afiliados.",

    'description': """
Este módulo engade como modelos aos Centros Educativos e aos Afiliados así como as relacións con estes, buscas e reportes.
    """,

    'author': "Marcos Chavarría Teijeiro",
    'website': "https://matesetal.gal",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/sindicato.especialidade.csv',
        'data/sindicato.tipo.cota.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

