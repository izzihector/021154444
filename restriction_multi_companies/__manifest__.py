# -*- coding: utf-8 -*-
{
    'name': "restriction_multi_companies",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account', 'product', 'uom'],
    "images": [
        'static/description/icon.png'
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/permissions.xml',
        'views/accounting_inherit.xml',
    ],
}
