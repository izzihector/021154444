# -*- coding: utf-8 -*-
{
    'name': 'Manual exchange rate',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Pragmatic SAS',
    'summary': 'This module allows the use of different types of exchange rates according to your need, the entry of the value of the rate is manually, that is, you enter the value that can be used in this case.',
    'website': 'http://www.pragmatic.com.co/',
    'version': '15.0.0.0',
    'license': 'OPL-1',
    'support': 'info@pragmatic.com.co',
    'price': '9.99',
    'currency': 'EUR',
    'images': ['static/description/TRM.jpg'],

    'depends': ['base', 'stock_landed_costs', 'sales_team', 'payment', 'portal'],
    'data': [
        'views/inventory_view/stock_landed_costs.xml',
        'views/invoice_view/client_invoice.xml',
        # 'views/invoice_view/payment _record.xml',
    ],
}
