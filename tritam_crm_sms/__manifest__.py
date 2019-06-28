# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Tri_Tam CRM SMS',
    'version': '1.0',
    'category': 'Base',
    'summary': 'Res Users',
    'description': """
""",
    'website': 'https://www.odoo.com',
    'depends': [
    	'base','crm','tritam_cpn_api','delivery'
    ],
    'data': [
            'views/crm_lead.xml',
            'views/sale_order.xml',
            'views/stock_picking.xml',
            'views/res_company.xml',
            'views/report_history_sms.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
