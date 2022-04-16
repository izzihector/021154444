# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Invoice EMI',
    'version': '15.0.0',
    'author': 'xetechs',
    'website': 'https://xetechs.com',
    'category': 'Account',
    'summary': 'Account Invoice EMI',
    'description': '''You can create Invoice EMI.
''',
    'depends': ['sale_management', 'purchase', 'account'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/account_invoice_emi_security.xml',
        'data/auto_create_invoice.xml',
        'data/product_data.xml',
        'security/ir.model.access.csv',
        'views/account_invoice_emi.xml',
        'views/sales_order.xml',
        'views/partner_view.xml',
    ],
    'sequence': 2,
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
