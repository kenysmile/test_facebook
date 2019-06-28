# -*- coding: utf-8 -*-
{
    'name': "DHC Button ",

    'summary': """""",

    'description': """
    """,

    'author': "Peter Lee",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','crm','tritam_automatic'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
    'qweb': ['static/src/xml2/button_kanban_template.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}