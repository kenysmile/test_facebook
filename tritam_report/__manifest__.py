# -*- coding: utf-8 -*-
{
    'name': "tritam_report",

    'summary': """
        Create menu link to metabase dashboard""",

    'description': """
        Tạo menu [Báo cáo] và config link dashboard của metabase vào odoo. Khi click menu [Báo cáo] thì redirect theo link đã config.
    """,

    'author': "Peter Lee",
    'website': "http://www.peterlee.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}