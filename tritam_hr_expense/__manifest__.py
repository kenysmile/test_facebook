# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Duoc Tri Tam Hr Expense',
    'version': '1.0',
    'category': 'hr_expense',
    'summary': 'hr_expense',
    'description': """
""",
    'website': 'https://www.odoo.com',
    'depends': [
    	'hr_expense','tritam_customer'
    ],
    'data': [
            'views/hr_expense.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
