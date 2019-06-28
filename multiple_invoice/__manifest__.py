# -*- coding: utf-8 -*-
{
    'name': "Multiple invoice",
	'category': 'Accounting',
    'summary': "Multiple invoice",
    'author': "Peter Lee",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/views.xml'
    ]
}