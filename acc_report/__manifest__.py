# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Analytic Account - Process Flow',
    'version': '15.0.0',
    'author': 'xetechs',
    'website': 'https://xetechs.com',
    'category': 'Account',
    'summary': '',
    'description': '''
''',
    'depends': ['analytic', 'account', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cost_center_view.xml',
        'wizard/account_report_wizard_view.xml',
        'wizard/account_general_ledger_view.xml',
        'views/account_analytic_account_view.xml',
        'views/account_account_view.xml',
        'views/default_process_flow_percentage_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
