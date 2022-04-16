# -*- coding: utf-8 -*-
# copyright Odoo SA
# Licence : LGPL-3

{
    'name': 'Cash report Session Summary',
    'version': '15.0.0.0.0',
    'category': 'Account',
    'summary': 'Adds a Session Summary PDF report on the Cash session',
    'author': 'osmincano@gmail.com',
    'license': 'LGPL-3',
    'depends': ['cash_session'],
    'data': [
        # 'session_summary_report.xml',
        'views/report_session_summary.xml',
    ],
    'installable': True,
    'application': False,
    'website': '',
    'auto_install': False,
}
