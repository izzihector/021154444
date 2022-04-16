# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Cancel Multiple Invoice',
    'version': '15.0.0.0.0',
    'category': 'Generic Modules/Others',
    'description': 'Allow To Cancel Multiple Invoice From the Tree View',
    'summary': 'Allow To Cancel Multiple Invoice From the Tree View',
    'author': 'Odoo Mates',
    'maintainer': 'Odoo Mates',
    'support': 'odoomates@gmail.com',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'account'
    ],
    'data': [
        'wizards/invoice_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
