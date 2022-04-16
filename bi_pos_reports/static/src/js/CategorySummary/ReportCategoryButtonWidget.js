
odoo.define('bi_pos_reports.ReportCategoryButtonWidget', function(require) {
	'use strict';

	const PosComponent = require('point_of_sale.PosComponent');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const { useListener } = require('web.custom_hooks');
	let core = require('web.core');
	let _t = core._t;
	const Registries = require('point_of_sale.Registries');


	class ReportCategoryButtonWidget extends PosComponent {
		constructor() {
			super(...arguments);
			useListener('click', this.onClick);
		}
			
		async onClick(){
			var self = this;
			self.showPopup('PopupCategoryWidget',{
				'title': 'Payment Summary',
			});
		}
	}


	ReportCategoryButtonWidget.template = 'ReportCategoryButtonWidget';
	ProductScreen.addControlButton({
		component: ReportCategoryButtonWidget,
		condition: function() {
			return this.env.pos.config.order_summery;
		},
	});
	Registries.Component.add(ReportCategoryButtonWidget);
	return ReportCategoryButtonWidget;
	
});