odoo.define('bi_pos_barcode_lot_selection.OrderWidgetExtended', function(require){
	'use strict';

	const OrderWidget = require('point_of_sale.OrderWidget');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { Component } = owl;

	const OrderSummaryExtended = (OrderWidget) =>
		class extends OrderWidget {
			constructor() {
				super(...arguments);
			}

			async _editPackLotLines(event) {
			    console.log("I called")
				const orderline = event.detail.orderline;
				let barcodes = this.env.pos.db.get_lot_barcode_by_prod_id(orderline.product.id);
				const isAllowOnlyOneLot = orderline.product.isAllowOnlyOneLot();
				const packLotLinesToEdit = orderline.getPackLotLinesToEdit(isAllowOnlyOneLot);
				const { confirmed, payload } = await this.showPopup('EditListPopup', {
					title: this.env._t('Lot/Serial Number(s) Required'),
					isSingleItem: isAllowOnlyOneLot,
					array: packLotLinesToEdit,
					product : orderline.product,
					barcodes : barcodes,
				});
				if (confirmed) {
					// Segregate the old and new packlot lines
					const modifiedPackLotLines = Object.fromEntries(
						payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
					);
					const newPackLotLines = payload.newArray
						.filter(item => !item.id)
						.map(item => ({ lot_name: item.text }));
					orderline.setPackLotLines({ modifiedPackLotLines, newPackLotLines });
				}
				this.order.select_orderline(event.detail.orderline);
			}
	};

	Registries.Component.extend(OrderWidget, OrderSummaryExtended);

	return OrderWidget;

});
