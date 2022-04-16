# -*- coding: utf-8 -*-
{
    'name': "Default Invoice Set on POS",
    'summary': """
        Default Invoice Set on POS""",
    'description': """
        Default Invoice Set on POS""",
    'author': 'iBOS Limited',
    'maintainer': 'Kamrul Hasan',
    'website': "https://www.ibos.io",
    'images': [],
    'category': 'Point Of Sale',
    'version': "15.0.1.0.0",
    'license': 'AGPL-3',
    'depends': [
        'base', 'point_of_sale'
    ],
    'data': [
    ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    'assets': {
                'point_of_sale.assets': [
                    'default_set_invoice_on_pos/static/src/js/default_invoice_payment.js',
                ]
            },
}
