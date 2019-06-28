# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Tri_Tam crm pipleline',
    'version': '1.0',
    'category': 'Base',
    'summary': 'Res Users',
    'description': """
""",
    'website': 'https://www.odoo.com',
    'depends': [
    	'base','sale',
    ],
    'data': [
            'data/data.xml',
            'views/schedule.xml',
            'views/view.xml',
            'views/update_tags.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
