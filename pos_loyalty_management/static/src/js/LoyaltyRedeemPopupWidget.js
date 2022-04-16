odoo.define('pos_loyalty_management.LoyaltyRedeemPopupWidget', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class LoyaltyRedeemPopupWidget extends AbstractAwaitablePopup {
		mounted(options){
			var self = this;
            super.mounted();
			this.options = options;
			setTimeout(function(){
				$('.move').addClass('complete');
			},500)
            $('.create_wallet').css({'pointer-events':'all'});
		}
        wk_click_cancel(){
            var currentOrder = this.env.pos.get_order();
            currentOrder.set('debit_points', 0);
            this.cancel();
        }
        loyalty_redeem_now() {
                var self = this;
                var currentOrder = self.env.pos.get_order();
                var discount_offer = currentOrder.get("discount_offer");
                var voucher_product_id = currentOrder.get("voucherProductId");
                var product = self.env.pos.db.get_product_by_id(voucher_product_id);
                if(product){
                    if(currentOrder.get("collapse")){
                        self.showPopup('confirm', {
                            'title': _t('Please confirm'),
                            'body': self.env.pos.get('loyalty_message')||_t('Fully redeem'),
                            confirm: function() {
                                currentOrder.set_client_loyal_points(currentOrder.get_client_loyal_points() - currentOrder.get('debit_points'));
                                currentOrder.add_product(product, { price: -discount_offer });
                                currentOrder.set('redeemTaken', true);
                                self.cancel();
                            },
                        });
                    }else{
                        currentOrder.set_client_loyal_points(currentOrder.get_client_loyal_points() - currentOrder.get('debit_points'));
                        currentOrder.add_product(product, { price: -discount_offer });
                        currentOrder.set('redeemTaken', true);
                        self.cancel();
                    }

                }else {
                    self.showPopup('WkLoyaltyAlertPopUp', {
                        'title': _t('Loyalty Redemption Error'),
                        'body': 'Sorry No Loyalty Product Found. Please create a loyalty product from backend!!!',
                    });
                }
            }
    }
    LoyaltyRedeemPopupWidget.template = 'LoyaltyRedeemPopupWidget';
    LoyaltyRedeemPopupWidget.defaultProps = {
        title: 'Confirm ?',
        body: '',
    };

    Registries.Component.add(LoyaltyRedeemPopupWidget);

    return LoyaltyRedeemPopupWidget;


});