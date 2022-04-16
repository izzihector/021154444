odoo.define('pos_network_printer.Multiprint', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var NetPrinter = require('pos_network_printer.Printer');
    var current_printer = new NetPrinter();

    models.Order = models.Order.extend({

        printChanges: async function () {
            var self = this;
            var printers = this.pos.printers;
            let isPrintSuccessful = true;
            for (var i = 0; i < printers.length; i++) {
                var changes = this.computeChanges(printers[i].config.product_categories_ids);
                if (changes['new'].length > 0 || changes['cancelled'].length > 0) {
                    var receipt = QWeb.render('OrderChangeReceipt', {changes: changes, widget: this});
                    if (printers[i].config.printer_type == "nt_printer") {
                        if (self.pos.config.printing_mode == 'offline') {
                            current_printer.print_offline_kot(self, receipt, printers[i].config);
                        }
                        if (self.pos.config.printing_mode == 'online') {
                            if (self.pos.config.connector == 'jspm') {
                                current_printer.print_jspm_kot(changes, printers[i].config);
                            }
                            if (self.pos.config.connector == 'websocket') {
                                current_printer.print_websocket_kot(self, receipt, printers[i].config);
                            }
                            if (self.pos.config.connector == 'printc') {
                                current_printer.print_online_kot(changes, printers[i].config);
                            }
                        }
                    } else {
                        const result = await printers[i].print_receipt(receipt);
                        if (!result.successful) {
                            isPrintSuccessful = false;
                        }
                    }
                }
            }
            return isPrintSuccessful;
        }

    });

});