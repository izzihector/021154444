# -*- coding: utf-8 -*-

{
    'name': "slm_invoice_advanced",

    'summary': """
        slm_invoice_advanced""",

    'description': """
        
    """,

    'author': "Xetechs S.A | Omar Flores oflores@xetechs.com",
    'website': "http://www.xetechs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': ['security/account_security.xml',
             'views/account_move_view.xml'
    ],
    'demo': [],
    'application': True,
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',

}