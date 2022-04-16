odoo.define('bi_pos_reports.XMLPosOrderSummaryReceipt', function(require) {
	'use strict';

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');

	class XMLPosOrderSummaryReceipt extends PosComponent {
		constructor() {
			super(...arguments);
		}
	}
	
	XMLPosOrderSummaryReceipt.template = 'XMLPosOrderSummaryReceipt';
	Registries.Component.add(XMLPosOrderSummaryReceipt);
	return XMLPosOrderSummaryReceipt;
});
