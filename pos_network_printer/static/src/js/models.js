odoo.define('pos_network_printer.Models', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var Printer = require('pos_network_printer.Printer');
    var _super = models.PosModel.prototype;

    models.load_models(
        [
            {
                model: 'network.printer',
                fields: ['printer_name', 'printer_ip', 'printer_port', 'connector_id'],
                domain: null,
                loaded: function (self, printers) {
                    var network_printers_config = {};
                    var network_printers_active = [];
                    for (var i = 0; i < self.config.network_printer_ids.length; i++) {
                        network_printers_config[self.config.network_printer_ids[i]] = true;
                    }
                    for (var i = 0; i < printers.length; i++) {
                        if (network_printers_config[printers[i].id]) {
                            network_printers_active.push(printers[i]);
                        }
                    }
                    self.network_printers = network_printers_active;
                },
            },
            {
                model: 'printer.connector',
                fields: ['id', 'token'],
                domain: null,
                loaded: function (self, connector) {
                    var printer_connectors = [];
                    for (var i = 0; i < connector.length; i++) {
                        printer_connectors.push(connector[i]);
                    }
                    self.printer_connectors = printer_connectors;
                }
            }
        ]
    );

    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var self = this;
            models.load_fields('restaurant.printer', ['printer_ip', 'printer_port', 'connector_id']);
            _super.initialize.apply(this, arguments);
            var newmodel = [];
            _.each(self.models, function (line) {
                if (line.model == 'restaurant.printer') {
                    line.loaded = function (self, printers) {
                        var active_printers = {};
                        for (var i = 0; i < self.config.printer_ids.length; i++) {
                            active_printers[self.config.printer_ids[i]] = true;
                        }
                        self.printers = [];
                        self.printers_categories = {};

                        for (var i = 0; i < printers.length; i++) {
                            if (active_printers[printers[i].id]) {
                                var printer = new Printer(self);
                                printer.config = printers[i];
                                self.printers.push(printer);
                                for (var j = 0; j < printer.config.product_categories_ids.length; j++) {
                                    self.printers_categories[printer.config.product_categories_ids[j]] = true;
                                }
                            }
                        }
                        self.printers_categories = _.keys(self.printers_categories);
                        self.config.iface_printers = !!self.printers.length;
                    }
                }
            });
        }
    });
});