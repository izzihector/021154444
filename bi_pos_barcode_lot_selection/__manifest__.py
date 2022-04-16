# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	"name" : "POS Auto Lot Selection With Barcode",
	"version" : "15.0.0.0",
	"category" : "Point of Sale",
	"summary": 'POS lot selection pos barcode lot selection on point of sale lot selection for pos automatic lot selection for point of sales lot selection pos unique lot selection point of sale unique lot selection pos serial number selection for point of sale serial',
	"description": """ This app helps to Create unique barcode-lot/serial number combination name , which will useful to print product labels based on lots/serial number , you can scan that on pos to add a product along with lot. This module allows you to select valid lot/serial number from selection field in Popup.We have also added validations to restrict user by adding wrong/not valid lot/serial number.User can also configure lot selection (based on Operation type location or from all locations.).""",
	"author": "BrowseInfo",
	"website" : "https://www.browseinfo.in",
	"price": 49,
	"currency": 'EUR',
	"depends" : ['base','product_expiry','point_of_sale', 'stock', 'ibos_erp_integration'],
	"data": [
		'report/product_label.xml',
		'views/product_view.xml',
		'views/pos_order_view.xml',
		'views/product_template.xml',
	],
	'assets': {
        'point_of_sale.assets': [
            "bi_pos_barcode_lot_selection/static/src/css/pos.css",
            "bi_pos_barcode_lot_selection/static/src/js/Popups/EditListPopup.js",
            "bi_pos_barcode_lot_selection/static/src/js/models.js",
            "bi_pos_barcode_lot_selection/static/src/js/Screens/OrderWidget.js",
            "bi_pos_barcode_lot_selection/static/src/js/Screens/ProductScreen.js",
            "bi_pos_barcode_lot_selection/static/src/js/Screens/ReceiptScreen.js",
        ],
        'web.assets_qweb': [
            'bi_pos_barcode_lot_selection/static/src/xml/pos.xml',
            'bi_pos_barcode_lot_selection/static/src/xml/OrderlineNew.xml',
        ],
     },
	"auto_install": False,
	"installable": True,
	"live_test_url":'https://youtu.be/LHwVmXe4Yt8',
	"images":["static/description/Banner.png"],
	'license': 'OPL-1',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
