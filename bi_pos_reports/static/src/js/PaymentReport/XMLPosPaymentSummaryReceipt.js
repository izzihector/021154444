odoo.define('bi_pos_reports.XMLPosPaymentSummaryReceipt', function(require) {
	'use strict';

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');

	class XMLPosPaymentSummaryReceipt extends PosComponent {
		constructor() {
			super(...arguments);
		}
	}
	
	XMLPosPaymentSummaryReceipt.template = 'XMLPosPaymentSummaryReceipt';
	Registries.Component.add(XMLPosPaymentSummaryReceipt);
	return XMLPosPaymentSummaryReceipt;
});
