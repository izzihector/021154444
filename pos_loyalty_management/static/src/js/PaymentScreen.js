odoo.define('pos_wechat.PaymentScreen', function (require) {
    'use strict';

    const { _t } = require('web.core');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    const PosWechatPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async _finalizeValidation() {
                var self = this;
                super._finalizeValidation();
                var current_order = self.env.pos.get_order();
                var partner = current_order.get_client();
                if(current_order && current_order.get('redeemTaken') && partner){
                    partner.wk_loyalty_points = partner.wk_loyalty_points -current_order.get('debit_points')+ current_order.get_loyalty_points();
                    current_order.set_client_loyal_points(current_order.get_client_loyal_points() + current_order.get_loyalty_points());
                }
                else if(current_order && partner && !current_order.get('redeemTaken')){
                    partner.wk_loyalty_points = partner.wk_loyalty_points + current_order.get_loyalty_points();
                    current_order.set_client_loyal_points(current_order.get_client_loyal_points() + current_order.get_loyalty_points());
                }
           }
        };

    Registries.Component.extend(PaymentScreen, PosWechatPaymentScreen);

    return PaymentScreen;
});
