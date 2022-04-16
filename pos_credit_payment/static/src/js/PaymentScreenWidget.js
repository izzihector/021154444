odoo.define('pos_credit_payment.PaymentScreenWidget', function(require){
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { Component } = owl;
	var rpc = require('web.rpc');

	const PaymentScreenWidget = (PaymentScreen) =>
		class extends PaymentScreen {
			constructor() {
				super(...arguments);
			}

			async validateOrder(isForceValidate) {
				var self = this;
				var currentOrder = this.env.pos.get_order();
				var plines = currentOrder.get_paymentlines();
				var dued = currentOrder.get_due();
				var changed = currentOrder.get_change();
				var clients = currentOrder.get_client();
				var a = [];
				var credit_total = 0;
				var pos_cur =  this.env.pos.config.currency_id[0];
				var company_id = this.env.pos.config.company_id;
				for(var i = 0; i < plines.length; i++) {
					if(plines[i].payment_method.credit_jr === true && (plines[i].payment_method.name === "Credit" || plines[i].payment_method.name === "credit")){
						a.push(plines[i]);
						credit_total += plines[i].get_amount()
					}
				}
				if(currentOrder.get_orderlines().length === 0){
					self.showPopup('ErrorPopup',{
						'title': this.env._t('Empty Order'),
						'body': this.env._t('There must be at least one product in your order before it can be validated.'),
					});
					return false;
				}
//				console.log("total credit amount is",credit_total)
				// Make Condition: Popup Occurs When Customer is not selected on credit_jr payment method, While any other payment method, this error popup will not be showing
				if (clients){  //if customer is selected
					if (a['length'] !== 0) { //we've given Miscellaneous Type
						if (credit_total > 0){
							if (!currentOrder.get_client()){
								self.showPopup('ErrorPopup',{
									'title': this.env._t('Unknown customer1'),
									'body': this.env._t('You cannot use Credit payment. Select customer first.'),
								});
								return false;
							}

							else if(currentOrder.get_change() > 0){ // Make Condition that amount is greater than selected customer's credit_jr amount
								self.showPopup('ErrorPopup',{
									'title': this.env._t('Payment Amount Exceeded'),
									'body': this.env._t('You cannot Pay More than Total Amount'),
								});
								return false;
							}
							else{
								var amount = credit_total
								self.rpc({
									model: 'res.partner',
									method: 'CheckCredit',
									args: [1,clients,company_id, pos_cur , amount]
								}).then(function(output) {
                                    if(clients.custom_credit < 0){
                                        var consumedCredit = (clients.credit_limit + clients.custom_credit).toFixed(2);
                                    }
                                    if(clients.custom_credit >= 0){
                                        var consumedCredit = (clients.credit_limit - clients.custom_credit).toFixed(2);
                                    }
//                                    console.log('output',output)
//                                    console.log('consumedCredit', consumedCredit)
//                                    console.log('currentOrder.get_paymentlines()', currentOrder.get_paymentlines())
								   if(output > consumedCredit){ // Make Condition that amount is greater than selected customer's credit_limit amount
										self.showPopup('ErrorPopup',{
											'title': self.env._t('Not Sufficient Credit'),
											'body': self.env._t('Customer has not Sufficient Credit To Pay'),
										});
										return false;
									}else
									{
										if (self._isOrderValid(isForceValidate)) {
											self.rpc({
												model: 'res.partner',
												method: 'UpdateCredit',
												args: [1,clients,company_id, pos_cur , amount],
												// args: [[client.id], {'custom_credit': updated}],
											}).then(function(output) {
												if(output==false){
													self.showPopup('ErrorPopup',{
														'title': this.env._t('Not Sufficient Credit'),
														'body': this.env._t('Customer has not Sufficient Credit To Pay'),
													});
													return false;
												}
												else{
                                                    if(self.currentOrder.get_due() === 0){
													   clients.custom_credit = clients.custom_credit - amount
													   self._finalizeValidation();
													}
												}
											});
										}
									}
								});
							}
						}
					}else{
						if (await this._isOrderValid(isForceValidate)) {
							// remove pending payments before finalizing the validation
							for (let line of this.paymentLines) {
								if (!line.is_done()) this.currentOrder.remove_paymentline(line);
							}
							await this._finalizeValidation();
						}
					}

					
				}
				else if(a['length'] == 0 && clients){
					if (await this._isOrderValid(isForceValidate)) {
						// remove pending payments before finalizing the validation
						for (let line of this.paymentLines) {
							if (!line.is_done()) this.currentOrder.remove_paymentline(line);
						}
						await this._finalizeValidation();
					}
				}
				else{
					self.showPopup('ErrorPopup',{
						'title': this.env._t('Alert'),
						'body': this.env._t('Select customer first.'),
					});
					return false;
				}       	                
			}
	};

	Registries.Component.extend(PaymentScreen, PaymentScreenWidget);

	return PaymentScreen;

});