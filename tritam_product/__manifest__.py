# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Duoc Tri Tam',
    'version': '1.0',
    'category': 'Product',
    'summary': 'Product',
    'description': """
""",
    'website': 'https://www.odoo.com',
    'depends': [
    	'product','stock'
    ],
    'data': [
            'views/product.xml',
            'views/product_price_list.xml',
            'views/product_product.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
