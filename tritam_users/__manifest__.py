# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Tri Tam Duoc Users',
    'version': '1.0',
    'category': 'Base',
    'summary': 'Res Users',
    'description': """
""",
    'website': 'https://www.odoo.com',
    'depends': [
    	'base', 'stock', 'hr', 'sale', 'sales_team', 'sale_stock'
    ],
    'data': [
            'data/data.xml',
            'views/users.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
