# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Inventory Adjustment Backdated",
    'category': 'Inventory',
    'version': '15.0.0.0',
    'author': 'Equick ERP',
    'description': """
        This Module allows user to do adjustments in back dated-force dated.
        * Allow user to do adjustments in back dated-force dated..
        * Update the date in stock moves and product moves.
        * Update the date in journal entries if product have automated valuation method.
    """,
    'summary': """inventory adjustment date | inventory adjustment force date | force date inventory adjustment | back dated inventory adjustment | date inventory adjustment | back dated inventory | force date inventory.""",
    'depends': ['stock_account'],
    'price': 12,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
