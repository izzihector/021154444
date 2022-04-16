# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'ibos Inventory Adjustment Approval',
    'version': '1.1',
    'summary': 'Test',
    'sequence': 30,
    'description': """ Inventory Adjustment Approval """,
    'category': 'Test',
    'website': '',
    'depends': ['stock'],
    'data': [
        'security/security.xml',
        'views/InventoryAdjustmentApproval.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
