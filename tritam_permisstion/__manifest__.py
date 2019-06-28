# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Phân quyền Tri Tâm',
    'version': '1.0',
    'category': 'Phân Quyền',
    'summary': 'Phân Quyền',
    'description': """
""",
    'website': 'https://www.odoo.com',
    'depends': ['base', 'tritam_users', 'crm', 'sale'],
    'data': [
            # 'views.xml',
            # 'data.xml',
            # 'views_conf_auto_share.xml',
            'security/ir.model.access.csv',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
