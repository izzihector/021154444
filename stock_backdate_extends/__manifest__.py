# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Inventory Adjustment Backdated -Extends-",
    'category': 'Inventory',
    'version': '15.0.0.0',
    'author': 'Xetechs, S.A.',
    'website': 'https://www.xetechs.com',
    'support': 'Luis Aquino -> laquino@xetechs.com',
    'description': """
        This Module allows user to do adjustments in back dated-force dated.
        * Allow user to do adjustments in back dated-force dated..
        * Update the date in stock moves and product moves.
        * Update the date in journal entries if product have automated valuation method.
    """,
    'summary': """inventory adjustment date | inventory adjustment force date | force date inventory adjustment | back dated inventory adjustment | date inventory adjustment | back dated inventory | force date inventory.""",
    'depends': ['eq_backdated_inventory_adjustment', 'branch'],
    'data': [
        'views/stock_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
