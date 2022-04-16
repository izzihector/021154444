odoo.define('default_set_invoice_on_pos.defaultInvoice', function (require){
    'use_strict';

    const { Gui } = require('point_of_sale.Gui');
    const PosComponent = require('point_of_sale.PosComponent');
    const { posbus } = require('point_of_sale.utils');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const defaultInvoicePaymentScreen = (PaymentScreen) =>
       class extends PaymentScreen {
            constructor() {
                super(...arguments);
                console.log("PaymentScreen::", PaymentScreen)

                // if (this.env.pos.getOnlinePaymentMethods().length !== 0) {
                //     useBarcodeReader({
                //         credit: this.credit_code_action,
                //     });
                // }
                // // How long we wait for the odoo server to deliver the response of
                // // a Vantiv transaction
                // this.server_timeout_in_ms = 95000;
                //
                // // How many Vantiv transactions we send without receiving a
                // // response
                // this.server_retries = 3;
            }
       };
    Registries.Component.extend(PaymentScreen, defaultInvoicePaymentScreen);
    return defaultInvoicePaymentScreen;
})