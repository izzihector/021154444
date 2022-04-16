/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_loyalty_management.CustomerRedeemButton', function(require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t; 
    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    const PaymentScreen = require('point_of_sale.PaymentScreen').prototype;
	var rpc = require('web.rpc')
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    console.log('before onclick');
    class CustomerRedeemButton extends PosComponent {

        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
            console.log('in constructor');

        }
        
        onClick(){
                
            var self = this;
            var order = this.env.pos.get_order();
            var client = order.get_client();
            var msg;
            if (client) {
                if (order.get_total_with_tax() > 0) {
                    if(self.env.pos.db.loyality_product_id){
                        if(!order.get('redeemTaken')) {
                            if(order.get_client_loyal_points()>0) {
                                if(order.get_client_loyal_points()>=self.env.pos.get('loyalty_min_points')) {
                                    var product_id = self.env.pos.db.loyality_product_id
                                    order.set('voucherProductId', product_id);
                                    rpc.query({
                                     model:'loyalty.management',
                                    method:'get_customer_loyality',
                                     args:[client.id, order.get_total_with_tax(), order.get_client_loyal_points()]
                                    })
                                    .catch(function(unused, event) {
                                        event.preventDefault();
                                        msg = _t('Failed to fetch customer loyalty points');
                                        self.loyalty_error_alert(msg);
                                    }).then(function(result) {
                                        var tpoints = result.points;
                                        var discount = result.discount;
                                    
                                        if (discount != -1) {
                                            if (discount != 0) {
                                                if (tpoints > 0 && order.get_client_loyal_points() > 0) {
                                                    var dueTotal = order.get_total_with_tax();
                                               
                                                   var discount_offer = dueTotal > discount ? discount : dueTotal;                                                
                                                    discount_offer = round_di(parseFloat(discount_offer) || 0, self.env.pos.dp['Product Price']);
                                                    order.set('discount_offer', discount_offer);
                                                    order.set('debit_points', result.debit_points);
                                                    order.set('collapse', result.collapse);
                                                    self.showPopup('LoyaltyRedeemPopupWidget', {
                                                        'name': client.name,
                                                        'points': tpoints < order.get_client_loyal_points() ? tpoints : order.get_client_loyal_points(),
                                                        'discount': discount_offer,
                                                    });
                                                } else {
                                                    self.loyalty_error_alert(_t('Sorry You Cannot Redeem, Because Customer Has 0 Points!!!'));
                                                }
                                            } else {
                                                self.loyalty_error_alert(_t('Sorry, You don`t have enough points to redeem !!!'));
                                            }

                                        } else {
                                            self.loyalty_error_alert(_t('Sorry No Redemption Calculation Found in Loyalty Rule. Please Add Redemption Rule First !!!'));
                                        }
                                    });
                                }else{
                                    self.loyalty_error_alert(_t('Sorry, You don`t have enough points to redeem !!! Minimum Points required to redeem are '+self.env.pos.get('loyalty_min_points')+' points.'));
                                }
                            }else{
                                self.loyalty_error_alert(_t('Sorry You Cannot Redeem, Because Customer Has 0 Points!!!'));
                            }
                        } else {
                            self.loyalty_error_alert(_t('Sorry You Have Already Redeemed Fidelity points for this customer!!!'));
                        }
                    }else{
                        self.loyalty_error_alert(_t('Failed to fetch Loyalty Product, Configure Loyalty Rules!!!'));
                    }
                } else {
                    if (order.orderlines.models.length && order.get('redeemTaken'))
                        self.loyalty_error_alert(_t('Sorry You Have Already Redeemed Fidelity points for this customer!!!'));
                    else
                        self.loyalty_error_alert(_t('Please add some Product(s) First !!!'));
                }
            } 
            else {
                const { confirmed } = this.showPopup('ConfirmPopup', {
                    title: this.env._t('Please select the Customer'),
                    body: this.env._t(
                        'You need to select the customer before you can redeem loyalty points.'
                    ),
                });
                if (confirmed) {
                    PaymentScreen.selectClient.call(self);
                    return false;
                }
            }
            
        }

        loyalty_error_alert(msg) {     
            var self = this;
            self.showPopup('WkLoyaltyAlertPopUp', {
                'title': self.env._t('Loyalty Redemption Error'),
                'body': msg,
            });
        }
    }
    CustomerRedeemButton.template = 'CustomerRedeemButton';
    ProductScreen.addControlButton({
        component: CustomerRedeemButton,
        condition: function () {
            return true;
        },
        
    });
    Registries.Component.add(CustomerRedeemButton);
    return CustomerRedeemButton;
});
