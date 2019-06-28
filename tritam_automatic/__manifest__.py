# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Phân bổ',
    'version': '1.0',
    'category': 'Partner Customer',
    'summary': 'Customer',
    'description': """
""",
    'website': 'https://www.odoo.com',
    'depends': ['base','tritam_customer','tritam_users'],
    'data': [
            'views.xml',
            'data.xml',
            'views_conf_auto_share.xml',
            'security/ir.model.access.csv',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
