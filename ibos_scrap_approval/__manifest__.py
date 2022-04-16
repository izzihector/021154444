# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'ibos Scrap Approval',
    'version': '1.1',
    'summary': 'Test',
    'sequence': 20,
    'description': """ Scrap Approval """,
    'category': 'Test',
    'website': '',
    'depends': ['mail',
                'stock'],
    'data': [
        'security/security.xml',
        'data/data.xml',
        'views/ScrapApproval.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
