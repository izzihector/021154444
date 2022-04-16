odoo.define('bi_pos_barcode_lot_selection.BiEditListPopup', function(require) {
	'use strict';

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { useExternalListener } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;

	const EditListPopup = require('point_of_sale.EditListPopup');

	const BiEditListPopup = (EditListPopup) =>
		class extends EditListPopup {
			constructor() {
				super(...arguments);
			}

			get barcodes(){
				return this.props.barcodes;
			}

			async selectLot(event){
				let lot = $('.barcode_selector').val();
				$('.list-line-input:last').text(lot);
				let arr = this.state.array;
				arr[arr.length-1].text = lot;
			}

			getPayload() {
				let self = this;
				let barcodes = this.barcodes;
				let lots = [];
				let res = true;


				$.each(barcodes, function( i, line ){
					lots.push(line.name)
				});

				let vals = {
					newArray: this.state.array
						.filter((item) => item.text.trim() !== '')
						.map((item) => Object.assign({}, item)),
				};

				console.log("vals:", vals)
				$.each(vals.newArray, function( i, line ){
					let is_valid = lots.indexOf(line.text);
					if(is_valid == -1 ){
						res = false;
						vals.newArray.splice(i, 1);
						alert("There are some invalid lot(s),Please add valid lot.")
					}
				});
				return vals;
			}

		}
	Registries.Component.extend(EditListPopup, BiEditListPopup);
	return BiEditListPopup;
});
