odoo.define('pos_network_printer.ScreenWidget', function (require) {
    'use strict';
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {_t} = require('web.core');
    const Registries = require('point_of_sale.Registries');
    const core = require('web.core');
    const QWeb = core.qweb;
    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const {useRef, useContext} = owl.hooks;
    var NetPrinter = require('pos_network_printer.Printer');


    const ReceiptScreenInherit = (ReceiptScreen) =>
        class extends ReceiptScreen {
            constructor() {
                super(...arguments);
                var self = this;
                if (this.env.pos.config.printing_mode == 'online' && this.env.pos.config.connector == 'jspm') {
                    JSPM.JSPrintManager.auto_reconnect = true;
                    var host = self.env.pos.config.client_app_ip;
                    var port = self.env.pos.config.client_app_port;
                    JSPM.JSPrintManager.start(true, host, port);
                }
            }

            async _printWeb() {
                try {
                    const self = this;
                    if (self.env.pos.config.ticket_print_mode == 'web') {
                        const isPrinted = document.execCommand('print', false, null);
                        if (!isPrinted) window.print();
                        return true;
                    } else {
                        self._printNetwork();
                        return true
                    }
                } catch (err) {
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Printing is not supported on some browsers'),
                        body: this.env._t(
                            'Printing is not supported on some browsers due to no default printing protocol ' +
                            'is available. It is possible to print your tickets by making use of an IoT Box.'
                        ),
                    });
                    return false;
                }
            }

            async _printNetwork() {
                var self = this;
                var current_printer = new NetPrinter();
                var printers = self.env.pos.network_printers;
                const receiptString = $('div.pos-receipt-container', self.el).html();
                const ticketImage = current_printer.htmlToImg(receiptString);

                var order = self.env.pos.get_order();
                var orderEnv = order.getOrderReceiptEnv();
                orderEnv.pos = self.env.pos;
                const receipt = QWeb.render('XmlReceipt', orderEnv);

                for (var i = 0; i < printers.length; i++) {
                    if (self.env.pos.config.printing_mode == 'offline') {
                        current_printer.print_offline(self, receipt, printers[i]);
                    }
                    if (self.env.pos.config.printing_mode == 'online') {
                        if (self.env.pos.config.connector == 'jspm') {
                            current_printer.print_jspm(self, ticketImage, printers[i]);
                        }
                        if (self.env.pos.config.connector == 'websocket') {
                            current_printer.print_websocket(self, receipt, printers[i]);
                        }
                        if (self.env.pos.config.connector == 'printc') {
                            current_print.print_online(self, printers[i]);
                        }
                    }


                }

            }
        };


    const ProductScreenInherit = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                var self = this;
                if (self.env.pos.config.printing_mode == 'online' && self.env.pos.config.connector == 'jspm') {
                    JSPM.JSPrintManager.auto_reconnect = true;
                    var host = self.env.pos.config.client_app_ip;
                    var port = self.env.pos.config.client_app_port;
                    JSPM.JSPrintManager.start(true, host, port);
                }
            }
        };

    Registries.Component.extend(ReceiptScreen, ReceiptScreenInherit);
    Registries.Component.extend(ProductScreen, ProductScreenInherit);

    return ReceiptScreen;
});