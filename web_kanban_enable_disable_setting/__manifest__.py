# -*- coding: utf-8 -*-
{
    'name': "Web Kanban enable/disable settings",

    'summary': """
        Kanban view grouped enable/disable setting""",

    'description': """
Add an attribute to the Kanban view group 
to enable or disable the setting displayed in the header view on hover on the title""",

    'author': "Hichri Selman",
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': ['base','web'],
    'data': [
        'views/assets.xml'
    ],
    'qweb': [
        'static/src/xml/web_kanban.xml'
    ],
}