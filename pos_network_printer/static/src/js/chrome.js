odoo.define('pos_network_printer.PrinterStatusWidget', function (require) {
    'use strict';

    // var pos_chrome = require('point_of_sale.chrome');
    // var models = require('point_of_sale.models');
    // var core = require('web.core');
    // var _t = core._t;
    // var _lt = core._lt;
    // var utils = require('web.utils');
    // var Mutex = utils.Mutex;
    // var Backbone = window.Backbone;
    //
    // var OrderCollection = Backbone.Collection.extend({
    //     model: models.Order,
    // });


    // var PrinterStatusWidget = pos_chrome.StatusWidget.extend({
    //     template: 'PrinterStatusWidget',
    //     start: function () {
    //         var self = this;
    //         self.check_all_printer();
    //         this.pos.bind('change:printer', function () {
    //             self.check_all_printer();
    //         });
    //         this.$el.click(function () {
    //             self.check_all_printer();
    //         });
    //     },
    //     check_printer: function (printer_ip, printer_port) {
    //         var self = this;
    //         self.set_status('connecting');
    //         var data = {
    //             "jsonrpc": "2.0",
    //             "params": {
    //                 "printer_ip": printer_ip,
    //                 "printer_port": printer_port,
    //             },
    //         }
    //         $.ajax({
    //             dataType: 'json',
    //             headers: {
    //                 "content-type": "application/json",
    //                 "cache-control": "no-cache",
    //             },
    //             url: '/check-printer',
    //             type: 'POST',
    //             proccessData: false,
    //             data: JSON.stringify(data),
    //             success: function (res) {
    //                 var data = JSON.parse(res.result);
    //                 if (data.error == 0) {
    //                     self.set_status('connected');
    //                     self.pos.set({printer: {state: 'connected'}});
    //                 } else {
    //                     self.set_status('disconnected');
    //                     self.pos.set({printer: {state: 'disconnected'}});
    //                 }
    //             }
    //         });
    //
    //     },
    //     check_all_printer: function () {
    //         var self = this;
    //         self.set_status('connecting');
    //         var network_printer = self.pos.config.network_printer_ids;
    //         if (network_printer.length == 0) {
    //             self.set_status('disconnected');
    //             self.pos.set({printer: {state: 'disconnected'}});
    //         } else {
    //             var data = {
    //                 "jsonrpc": "2.0",
    //                 "params": {
    //                     "ids": network_printer,
    //                 },
    //             }
    //             $.ajax({
    //                 dataType: 'json',
    //                 headers: {
    //                     "content-type": "application/json",
    //                     "cache-control": "no-cache",
    //                 },
    //                 url: '/check-all-printer',
    //                 type: 'POST',
    //                 proccessData: false,
    //                 data: JSON.stringify(data),
    //                 success: function (res) {
    //                     var data = JSON.parse(res.result);
    //                     if (data.error == 0) {
    //                         self.set_status('connected');
    //                         self.pos.set({printer: {state: 'connected'}});
    //                     } else {
    //                         self.set_status('disconnected');
    //                         self.pos.set({printer: {state: 'disconnected'}});
    //                     }
    //                 }
    //             });
    //         }
    //
    //     }
    // });
    //
    // var SpoolerStatusWidget = pos_chrome.StatusWidget.extend({
    //     template: 'SpoolerStatusWidget',
    //     start: function () {
    //         var self = this;
    //         self.check_receipt_queue();
    //         this.pos.bind('change:spooler', function () {
    //             if (self.pos.get('spooler').state == 'connecting') {
    //                 self.check_receipt_queue();
    //             }
    //         });
    //         this.$el.click(function () {
    //             self.set_status('connecting');
    //             self.print_receipt_queue();
    //         });
    //     },
    //     check_receipt_queue: function () {
    //         var unprinted_receipt = this.pos.db.load('receipt', []);
    //         if (unprinted_receipt.length > 0) {
    //             this.set_status('error');
    //             this.pos.set({spooler: {state: 'error'}});
    //         } else {
    //             this.set_status('connected');
    //             this.pos.set({spooler: {state: 'connected'}});
    //         }
    //     },
    //     print_receipt_queue: function () {
    //         var self = this;
    //         var receipt = this.pos.db.load('receipt', []);
    //
    //         var print_receipt = function (receipt) {
    //             if (receipt.length > 0) {
    //                 var current_receipt = receipt.shift();
    //                 var receipt_data = {
    //                     "uid": current_receipt.uid,
    //                     "printer_ip": current_receipt.printer_ip,
    //                     "printer_port": current_receipt.printer_port,
    //                     "receipt": current_receipt.receipt,
    //                 }
    //                 var json_data = {
    //                     "jsonrpc": "2.0",
    //                     "params": receipt_data
    //                 }
    //
    //                 $.ajax({
    //                     dataType: 'json',
    //                     headers: {
    //                         "content-type": "application/json",
    //                         "cache-control": "no-cache",
    //                     },
    //                     url: '/print-network-xmlreceipt',
    //                     type: 'POST',
    //                     proccessData: false,
    //                     data: JSON.stringify(json_data),
    //                     success: function (res) {
    //                         var data = JSON.parse(res.result);
    //                         if (data.error == 1) {
    //                             receipt.unshift(current_receipt);
    //                         }
    //                         self.pos.db.save('receipt', receipt);
    //                         self.check_receipt_queue();
    //                     }
    //                 });
    //
    //             } else {
    //                 self.set_status('connected');
    //                 self.pos.set({spooler: {state: 'connected'}});
    //                 return
    //             }
    //             // print_receipt(receipt);
    //         }
    //         print_receipt(receipt);
    //     }
    // });
    //
    // pos_chrome.Chrome.include({
    //     build_widgets: function () {
    //         var element = _.find(this.widgets, function (w) {
    //             return w.name === 'notification';
    //         });
    //         var index = this.widgets.indexOf(element);
    //         this.widgets.splice(index + 1, 0, {
    //             'name': 'spooler_status',
    //             'widget': SpoolerStatusWidget,
    //             'append': '.pos-rightheader',
    //         }, {
    //             'name': 'printer_status',
    //             'widget': PrinterStatusWidget,
    //             'append': '.pos-rightheader',
    //         });
    //
    //         this._super();
    //     },
    // });
});
