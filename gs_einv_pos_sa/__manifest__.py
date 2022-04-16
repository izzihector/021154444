# -*- coding: utf-8 -*-

{
    "name": "gs_einv_pos_sa",
    "version": "15.0.0.0.2",
    'depends': ['base', 'point_of_sale'],
    "author": "Global Solutions",
    "category": "Point of Sale",
    "website": "https://globalsolutions.dev",
    "images": ["static/description/assets/main_screenshot.gif"],
    "price": "0",
    "license": "OPL-1",
    "currency": "USD",
    "summary": "e-Invoice KSA POS ",
    "data": [
        'views/template.xml',

    ],
    "qweb": [
        "static/src/xml/pos_receipt.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    'assets': {
        'point_of_sale.assets': [
            'gs_einv_pos_sa/static/src/js/qrcode.js',
            'gs_einv_pos_sa/static/src/js/models.js',
        ],
        'web.assets_qweb': [
            'gs_einv_pos_sa/static/src/xml/**/*',
        ],
    },
}
