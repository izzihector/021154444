# -*- coding: utf-8 -*-
{
    'name': "EasyERPS POS Custom",
    'support': "support@easyerps.com",
    'license': "OPL-1",
    'price': 150,
    'currency': "SR",
    'summary': """
        This module Allows you to print POS custom receipts 
        """,



    'author': "Easyerps",
    'website': "www.EasyERPS.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'web/static/lib/zxing-library/zxing-library.js',
            'EasyERPS_pos_custom/static/src/js/ReceiptScreen.js',
            'EasyERPS_pos_custom/static/src/js/Models.js',
            'EasyERPS_pos_custom/static/src/js/pos_refund_sequence.js',
            'EasyERPS_pos_custom/static/src/css/OrderReceipt.css',
        ],
        'web.assets_qweb': [
            'EasyERPS_pos_custom/static/src/xml/OrderReceipt.xml',
            'EasyERPS_pos_custom/static/src/xml/ProductScreen.xml',
        ],

    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
