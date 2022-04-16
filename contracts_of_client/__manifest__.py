# -*- coding: utf-8 -*-

{
    'name': 'Contratos de Cliente',
    'version': '15.0',
    'author': "Xetechs, S.A.",
    'website': 'https:/www.xetechs.com',
    'support': 'Juan Carlos Rojas --> jrojas@xetechs.com',
    'sequence': 1,
    'license':'OPL-1',
    'depends': [
        'sale',
        'sale_management',
        'product',
        'base'
    ],
    'data': [
        'security/groups.xml',
        'views/product_pricelist_views.xml',
        'views/sale_views.xml',
        'views/contracts_views.xml',
        'data/ir_sequence_data.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}