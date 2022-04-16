# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	"name" : "ALL POS Reports in Odoo (POS BOX Compatible)",
	"version" : "15.0.0.0",
	"category" : "Point of Sale",
	"depends" : ['base','sale','point_of_sale'],
	"author": "BrowseInfo",
	'summary': 'All in one pos reports Print pos session report pos sales summery report pos sales reports point of sales reports pos X Report pos z report pos payment summary reports pos Inventory audit report pos Order summary report pos Posted Session POS Profit Report',
	"description": """
	odoo Print POS Reports print pos reports odoo all in one pos reports
    odoo point of sales reports pos reports print pos report print
	odoo pos sales summary report pos summary report pos Session and Inventory audit report
    odoo pos audit report pos Product summary report
     odoo pos sessions reports pos session reports pos User wise sales summary reports
     odoo pos payment summary reports summary reports in POS
     odoo point of sales summary reports point of sales reports pos user reports
     odoo point of sales all reports pos products reports pos audit reports audit reports pos 
	odoo pos Inventory audit reports pos Inventory reports Product summary report pos 

		odoo Print point of sales Reports print point of sales reports odoo all in one point of sales reports
    odoo point of sale reports point of sales reports print point of sales report print
	odoo point of sale summary report point of sales summary report point of sales Session and Inventory audit report
    odoo point of sales audit report point of sale Product summary report
     odoo point of sales sessions reports point of sales session reports point of sales User wise sales summary reports
     odoo pos payment summary reports summary reports in POS
     odoo point of sales summary reports point of sales reports point of sales user reports
     odoo point of sale all reports point of sales products reports point of sales audit reports audit reports point of sales 
	odoo point of sales Inventory audit reports point of sales Inventory reports Product summary report point of sales 

	""",
	"website" : "https://www.browseinfo.in",
	"price": 39,
	"currency": "EUR",
	"data": [
		'security/ir.model.access.csv',
		'views/pos_reports.xml',
		'wizard/sales_summary_report.xml',
		'wizard/pos_sale_summary.xml',
		'wizard/x_report_view.xml',
		'wizard/z_report_view.xml',
		'wizard/top_selling.xml',
		'wizard/top_selling_report.xml',
		'wizard/profit_loss_report.xml',
		'wizard/pos_payment_report.xml',
		'wizard/profit_loss.xml',
		'wizard/pos_payment.xml',
	],
	'assets': {
		'point_of_sale.assets': [
			'bi_pos_reports/static/src/css/reports.css',
			'bi_pos_reports/static/src/js/models.js',
			'bi_pos_reports/static/src/js/AuditReport/ReportLocationButtonWidget.js',
			'bi_pos_reports/static/src/js/AuditReport/PopupLocationWidget.js',
			'bi_pos_reports/static/src/js/AuditReport/LocationReceiptScreen.js',
			'bi_pos_reports/static/src/js/AuditReport/LocationReceipt.js',
			'bi_pos_reports/static/src/js/CategorySummary/ReportCategoryButtonWidget.js',
			'bi_pos_reports/static/src/js/CategorySummary/PopupCategoryWidget.js',
			'bi_pos_reports/static/src/js/CategorySummary/CategoryReceiptWidget.js',
			'bi_pos_reports/static/src/js/CategorySummary/XMLPosCategorySummaryReceipt.js',
			'bi_pos_reports/static/src/js/OrderSummary/ReportOrderButtonWidget.js',
			'bi_pos_reports/static/src/js/OrderSummary/PopupOrderWidget.js',
			'bi_pos_reports/static/src/js/OrderSummary/OrderReceiptWidget.js',
			'bi_pos_reports/static/src/js/OrderSummary/XMLPosOrderSummaryReceipt.js',
			'bi_pos_reports/static/src/js/PaymentReport/ReportPaymentButtonWidget.js',
			'bi_pos_reports/static/src/js/PaymentReport/PaymentSummaryPopup.js',
			'bi_pos_reports/static/src/js/PaymentReport/PaymentReceiptWidget.js',
			'bi_pos_reports/static/src/js/PaymentReport/XMLPosPaymentSummaryReceipt.js',
			'bi_pos_reports/static/src/js/ReportProductButton/ReportProductButtonWidget.js',
			'bi_pos_reports/static/src/js/ReportProductButton/PopupProductWidget.js',
			'bi_pos_reports/static/src/js/ReportProductButton/ProductReceiptWidget.js',
			'bi_pos_reports/static/src/js/ReportProductButton/XMLPosProductSummaryReceipt.js',
		],
		'web.assets_qweb': [
			'bi_pos_reports/static/src/xml/**/*',
		],
	},
	"auto_install": False,
	"installable": True,
	"images":['static/description/Banner.png'],
	"live_test_url":'https://youtu.be/Y5t_EZJxymY',
	'license': 'OPL-1',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
