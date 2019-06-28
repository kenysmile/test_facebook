# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Duoc Tri Tam Sale',
    'version': '1.0',
    'category': 'Sale',
    'summary': 'Sale',
    'description': """This module customize from module sale""",
    'website': 'https://www.odoo.com',
    'depends': [
    	'base','sale','tritam_customer','tritam_users',
        'sale_order_dates','delivery','hr_expense',
        'tritam_cpn_api','multiple_invoice',
    ],
    'data': [
        'views/so_view.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
