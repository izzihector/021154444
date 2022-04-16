odoo.define('pos_network_printer.Printer', function (require) {
    'use strict';
    var core = require('web.core');
    var Registries = require('point_of_sale.Registries');
    var mixins = require('point_of_sale.Printer');

    var Printer = core.Class.extend(mixins.PrinterMixin, {
        init: function () {
            mixins.PrinterMixin.init.call(this, arguments);
            this.widget = this;
        },
        jspmWSStatus: function () {
            if (JSPM.JSPrintManager.websocket_status == JSPM.WSStatus.Open)
                return true;
            else if (JSPM.JSPrintManager.websocket_status == JSPM.WSStatus.Closed) {
                console.warn('JSPrintManager (JSPM) is not installed or not running! Download JSPM Client App from https://neodynamic.com/downloads/jspm');
                return false;
            }
            else if (JSPM.JSPrintManager.websocket_status == JSPM.WSStatus.Blocked) {
                alert('JSPM has blocked this website!');
                return false;
            }
        },

        print_offline: function (widget, receipt, printer) {
            var self = this;
            var order = widget.env.pos.get_order();
            var receipt_data = {
                "uid": order.uid,
                "printer_ip": printer.printer_ip,
                "printer_port": printer.printer_port,
                "receipt": receipt
            };
            var receipt_db = widget.env.pos.db.load('receipt', []);
            receipt_db.push(receipt_data);
            widget.env.pos.db.save('receipt', receipt_db);

            var data = {
                "jsonrpc": "2.0",
                "params": receipt_data
            }
            $.ajax({
                dataType: 'json',
                headers: {
                    "content-type": "application/json",
                    "cache-control": "no-cache",
                },
                url: '/print-network-xmlreceipt',
                type: 'POST',
                proccessData: false,
                data: JSON.stringify(data),
                success: function (res) {
                    var data = JSON.parse(res.result);
                    if (data.error == 0) {
                        self.remove_printed_order(widget, data.uid);
                    }
                    if (data.error == 1) {
                        widget.pos.set({printer: {state: 'disconnected'}, spooler: {state: 'connecting'}});
                    }
                }
            });
        },
        print_online: function (widget, printer) {
            var self = this;
            var order = widget.env.pos.get_order();
            var queue_print_data = {
                "printer_name": printer.printer_name,
                "printer_ip": printer.printer_ip,
                "printer_port": printer.printer_port,
                "connector_id": printer.connector_id[0],
                "receipt": receipt,
                "token": self.get_connector_token(widget, printer),
            }
            widget.env.pos.rpc({
                model: 'queue.print',
                method: 'create',
                args: [queue_print_data]
            }).then(function (result) {
                console.log('new queue created ' + 1);
            });
        },
        print_jspm: function (widget, ticketImage, printer) {
            var self = this;
            var escpos = Neodynamic.JSESCPOSBuilder;
            var doc = new escpos.Document();

            ticketImage.then(function (b64img) {
                escpos.ESCPOSImage.load("data:image/png;base64," + b64img).then(img => {
                    var escposCommands = doc
                        .image(img)
                        .feed(5)
                        .cut()
                        .generateUInt8Array();

                    if (self.jspmWSStatus()) {
                        var myPrinter = new JSPM.NetworkPrinter(parseInt(printer.printer_port), printer.printer_ip, printer.printer_name);
                        var cpj = new JSPM.ClientPrintJob();
                        cpj.clientPrinter = myPrinter;
                        cpj.binaryPrinterCommands = escposCommands;
                        cpj.sendToClient();
                    }
                })

            });

        },
        remove_printed_order: function (widget, uid) {
            var receipt_db = widget.env.pos.db.load('receipt', []);
            var printed_receipt = receipt_db.pop();
            if (printed_receipt.uid != uid) {
                receipt.push(printed_receipt);
            }
            widget.env.pos.db.save('receipt', receipt_db);
        },
        get_connector_token: function (widget, printer) {
            var connector = _.filter(widget.env.pos.printer_connectors, function (line) {
                return line.id == printer.connector_id[0]
            });
            return connector[0].token;
        },
        print_offline_kot: function (widget, receipt, printer) {
            var self = this;
            var order = widget.pos.get_order();
            var receipt_data = {
                "uid": order.uid,
                "printer_ip": printer.printer_ip,
                "printer_port": printer.printer_port,
                "receipt": receipt
            };
            var receipt_db = widget.pos.db.load('receipt', []);
            receipt_db.push(receipt_data);
            widget.pos.db.save('receipt', receipt_db);

            var data = {
                "jsonrpc": "2.0",
                "params": receipt_data
            }
            $.ajax({
                dataType: 'json',
                headers: {
                    "content-type": "application/json",
                    "cache-control": "no-cache",
                },
                url: '/print-network-xmlreceipt',
                type: 'POST',
                proccessData: false,
                data: JSON.stringify(data),
                success: function (res) {
                    var data = JSON.parse(res.result);
                    if (data.error == 0) {
                        self.remove_printed_order_kot(widget, data.uid);
                    }
                    if (data.error == 1) {
                        widget.pos.set({printer: {state: 'disconnected'}, spooler: {state: 'connecting'}});
                    }
                }
            });
        },
        print_online_kot: function (changes, printer) {
            var self = this;
            var order = widget.pos.get_order();
            var queue_print_data = {
                // "uid": order.uid,
                "printer_name": printer.name,
                "printer_ip": printer.printer_ip,
                "printer_port": printer.printer_port,
                "connector_id": printer.connector_id[0],
                "receipt": receipt,
                "token": self.get_connector_token_kot(widget, printer),
            }
            widget.pos.rpc({
                model: 'queue.print',
                method: 'create',
                args: [queue_print_data]
            }).then(function (result) {
                console.log('new queue created ' + 1);
            });
        },
        print_jspm_kot: function (changes, printer) {
            var self = this;
            var escpos = Neodynamic.JSESCPOSBuilder;
            var doc = new escpos.Document();
            var escposCommands = doc
                .font(escpos.FontFamily.A)
                .align(escpos.TextAlignment.Center)
                .size(0, 0)
                .text(changes.name + ' ' + changes.time.hours + ':' + changes.time.minutes);

            if (changes.new.length > 0) {
                escposCommands = escposCommands
                    .align(escpos.TextAlignment.LeftJustification)
                    .size(1, 1)
                    .text('NEW');
            }
            for (var i = 0; i < changes.new.length; i++) {
                escposCommands = escposCommands
                    .size(0, 0)
                    .drawTable([changes.new[i].name, changes.new[i].qty])
            }
            escposCommands = escposCommands.text(' ');
            if (changes.cancelled.length > 0) {
                escposCommands = escposCommands
                    .align(escpos.TextAlignment.LeftJustification)
                    .size(1, 1)
                    .text('CANCELLED');
            }
            for (var i = 0; i < changes.cancelled.length; i++) {
                escposCommands = escposCommands
                    .size(0, 0)
                    .drawTable([changes.cancelled[i].name, changes.cancelled[i].qty])
            }

            escposCommands = escposCommands
                .feed(3)
                .cut()
                .generateUInt8Array();

            if (self.jspmWSStatus()) {
                var myPrinter = new JSPM.NetworkPrinter(parseInt(printer.printer_port), printer.printer_ip, printer.printer_name);
                var cpj = new JSPM.ClientPrintJob();
                cpj.clientPrinter = myPrinter;
                cpj.binaryPrinterCommands = escposCommands;
                cpj.sendToClient();
            }
        },
        print_websocket: function (widget, receipt, printer) {
            var self = this;
            var receipt_data = JSON.stringify({
                "printer_ip": printer.printer_ip,
                "printer_port": printer.printer_port,
                "xmlreceipt": receipt,
                "origin": window.location.origin,
            });
            var client_app_ip = widget.env.pos.config.client_app_ip;
            var client_app_port = widget.env.pos.config.client_app_port;
            var url = "http://"+client_app_ip+":"+client_app_port;
            console.log('print using websocket '+url);
            var app_headers = new Headers();
            app_headers.append("Access-Control-Allow-Origin", "*");
            app_headers.append("Content-Type", "application/json");
            var requestOptions = {
                method: 'POST',
                headers: app_headers,
                mode: 'no-cors',
                body: receipt_data,
                redirect: 'follow'
            };
            fetch(url, requestOptions)
                .then(response => response.text())
                .then(result => console.log(result))
                .catch(error => console.log('error', error));
        },
        print_websocket_kot: function (widget, receipt, printer) {
            var self = this;
            console.log('print using web socket');
            console.log(widget);
            var receipt_data = JSON.stringify({
                "printer_ip": printer.printer_ip,
                "printer_port": printer.printer_port,
                "xmlreceipt": receipt,
                "origin": window.location.origin,
            });
            var client_app_ip = widget.pos.config.client_app_ip;
            var client_app_port = widget.pos.config.client_app_port;
            var url = "http://"+client_app_ip+":"+client_app_port;
            var app_headers = new Headers();
            app_headers.append("Access-Control-Allow-Origin", "*");
            app_headers.append("Content-Type", "application/json");

            var requestOptions = {
                method: 'POST',
                headers: app_headers,
                mode: 'no-cors',
                body: receipt_data,
                redirect: 'follow'
            };

            fetch(url, requestOptions)
                .then(response => response.text())
                .then(result => console.log(result))
                .catch(error => console.log('error', error));
        },
        remove_printed_order_kot: function (widget, uid) {
            var receipt_db = widget.pos.db.load('receipt', []);
            var printed_receipt = receipt_db.pop();
            if (printed_receipt.uid != uid) {
                receipt.push(printed_receipt);
            }
            widget.pos.db.save('receipt', receipt_db);
        },
        get_connector_token_kot: function (widget, printer) {
            var connector = _.filter(widget.pos.printer_connectors, function (line) {
                return line.id == printer.connector_id[0]
            });
            return connector[0].token;
        },

    });

    Registries.Component.add(Printer);

    return Printer;
});