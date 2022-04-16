# -*- coding: utf-8 -*-

{
    'name': "SLM import utils",

    'summary': """
        This module is a set of tools for view, import and search data in the slm table""",

    'description': """
        This module is a set of tools for view, import and search data in the slm table
    """,

    'author': "Xetechs S.A | José Luis Regalado jregalado@xetechs.com",
    'website': "http://www.xetechs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],

    'demo': [],

    'application': True,

    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',

}
