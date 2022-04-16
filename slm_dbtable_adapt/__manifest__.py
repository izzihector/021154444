# -*- coding: utf-8 -*-
{
    'name': "[SLM] Database Table Adapter for Data Import",

    'summary': """
        This modules extends the model of other modules, in order to load data from other systems.""",

    'description': """
        This modules extends the model of other modules, in order to load data from other systems.
    """,

    'author': "Jose Luis Regalado | jregalado@xetechs.com",
    'website': "https://www.xetechs.com",

    'category': 'Accounting & Finance',
    'version': '0.1',
    'depends': ['base', 'account'],

    'data': [
        'views/account_invoice_view.xml',
        'views/account_journal_view.xml',
    ],
    'demo': [],

    'sequence': 1,
    'installable': True,
    'auto_install': False,

}