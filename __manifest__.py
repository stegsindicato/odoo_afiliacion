# -*- coding: utf-8 -*-
{
    'name': "STEG: Centros e Afiliación",

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
    'version': '0.2',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'partner_firstname', 'partner_contact_birthdate'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/sindicato.especialidade.csv',
        'data/sindicato.tipo.cota.csv',
        'data/cron.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

