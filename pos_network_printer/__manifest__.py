# -*- coding: utf-8 -*-
{
    'name': "POS NETWORK PRINTER",
    'summary': """
        Print from Point of sale to ESC/POS Network Printer without POS Box. The module is used for POS Retail and Restaurant with 
        with local or online server
        """,
    'description': """
        Print from Point of sale to ESC/POS Network Printer without POS Box. The module is used for POS Retail and Restaurant with 
        with local or online server.
    """,
    'author': "Aimé Jules Andrinirina",
    'website': 'https://www.aimejules.com',
    'license': 'OPL-1',
    'category': 'Point Of Sale',
    'version': '1.0',
    'images': ['static/description/banner.jpg'],
    'depends': [
        'base',
        'point_of_sale',
        'pos_restaurant',
        'pos_epson_printer',
        'pos_epson_printer_restaurant',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'assets': {
        'point_of_sale.assets': [
            '/pos_network_printer/static/src/lib/cptable.js',
            '/pos_network_printer/static/src/lib/cputils.js',
            '/pos_network_printer/static/src/lib/deflate.js',
            '/pos_network_printer/static/src/lib/JSESCPOSBuilder.js',
            '/pos_network_printer/static/src/lib/JSPrintManager.js',
            '/pos_network_printer/static/src/js/models.js',
            '/pos_network_printer/static/src/js/printer.js',
            '/pos_network_printer/static/src/js/chrome.js',
            '/pos_network_printer/static/src/js/screens.js',
            '/pos_network_printer/static/src/js/multiprint.js',
        ],
        'web.assets_qweb': [
            'pos_network_printer/static/src/xml/*',
        ],
    },

    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',
        # views
        'views/pos_config_view.xml',
        'views/network_printer_view.xml',
        'views/restaurant_printer_view.xml',
        'views/printer_connector_view.xml',
        'views/queue_print_view.xml',
    ],
    'price': '350',
    'currency': 'EUR',

}
