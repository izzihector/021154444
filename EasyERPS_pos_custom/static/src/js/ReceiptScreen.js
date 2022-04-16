odoo.define('pos_qr_code.ReceiptScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const customReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
            constructor() {
                super(...arguments);
                const order = this.currentOrder;
                window.onbeforeunload = function (e) {
                    order.finalize();

                };
            }

            // orderDone() {
            //     window.onbeforeunload = function (e) {
            //     };
            //     this.currentOrder.finalize();
            //     const { name, props } = this.nextScreen;
            //     this.showScreen(name, props);
            // }



        };

    Registries.Component.extend(ReceiptScreen, customReceiptScreen);

    return ReceiptScreen;
});