# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Cash Session',
    'version': '1.0.1',
    'category': 'Account',
    'sequence': 15,
    'author': 'Osmin Cano --> osmincano@gmail.com',
    'summary': 'Cash Session payments partners and suppliers',
    'description': "",
    'depends': ['account'],
    'data': [
        'security/cash_session_security.xml',
        'security/ir.model.access.csv',
        #'wizard/cash_box.xml',
        'views/cash_session_view.xml',
        'views/cash_config_view.xml',
        'views/cash_session_sequence.xml',
        'views/account_statement_view.xml',
        'views/account_payment_view.xml',
		'views/cashbox_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}
