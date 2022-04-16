odoo.define('pos_network_printer.BillScreenWidget', function (require) {
    // 'use strict';
    // var screens = require('point_of_sale.screens');
    // var core = require('web.core');
    // var QWeb = core.qweb;
    // var NetworkDevices = require('pos_network_printer.NetworkDevices');
    // var gui = require('point_of_sale.gui');
    //
    // var BillScreenWidget = screens.ReceiptScreenWidget.extend({
    //     template: 'BillScreenWidget',
    //     click_next: function () {
    //         this.gui.show_screen('products');
    //     },
    //     click_back: function () {
    //         this.gui.show_screen('products');
    //     },
    //     render_receipt: function () {
    //         this._super();
    //         this.$('.receipt-paymentlines').remove();
    //         this.$('.receipt-change').remove();
    //     },
    //     print_web: function () {
    //         var bill_print_mode = this.pos.config.bill_print_mode;
    //         if (bill_print_mode == 'web') {
    //             window.print();
    //         }
    //         if (bill_print_mode == 'network') {
    //             this.print_network();
    //         }
    //     },
    //     print_network: function () {
    //         var self = this;
    //         var printers = this.pos.network_printers;
    //         var order = this.pos.get('selectedOrder');
    //         if (order.get_orderlines().length > 0) {
    //             var receipt = order.export_for_printing();
    //             _.each(receipt.orderlines, function (line) {
    //                 // quantity
    //                 var nb = String(line.quantity);
    //                 if (nb.length == 1) {
    //                     line.quantity_nb = '<pre>  ' + line.quantity + '</pre>';
    //                 }
    //                 else if (nb.length == 2) {
    //                     line.quantity_nb = '<pre> ' + line.quantity + '</pre>';
    //                 }
    //                 else if (nb.length == 3) {
    //                     line.quantity_nb = line.quantity;
    //                 }
    //
    //                 //product_name
    //                 var product_nb = line.product_name_wrapped[0].length;
    //                 var max_nb = 20;
    //                 var final_product = "";
    //                 if (product_nb >= max_nb) {
    //                     for (var i = 0; i < max_nb; i++) {
    //                         final_product = final_product + line.product_name_wrapped[0][i];
    //                     }
    //                 } else {
    //                     var diff_nb = max_nb - product_nb;
    //                     final_product = '<pre>' + line.product_name_wrapped[0];
    //                     for (var i = 0; i < diff_nb; i++) {
    //                         final_product = final_product + ' ';
    //                     }
    //                     final_product = final_product + '</pre>';
    //                 }
    //                 line.final_product = final_product;
    //
    //                 //price unit
    //                 var max_pu_nb = 7;
    //                 var pu_nb = String(line.price).length;
    //                 var diff_pu_nb = max_pu_nb - pu_nb;
    //                 var final_pu = "<pre>";
    //                 for (var i = 0; i < diff_pu_nb; i++) {
    //                     final_pu = final_pu + ' ';
    //                 }
    //                 final_pu = final_pu + line.price + '</pre>';
    //                 line.final_pu = final_pu;
    //
    //                 //price display
    //                 var max_pd_nb = 10;
    //                 var pd_nb = String(line.price_display).length;
    //                 var diff_pd_nb = max_pd_nb - pd_nb;
    //                 var final_pd = "<pre>";
    //                 for (var i = 0; i < diff_pd_nb; i++) {
    //                     final_pd = final_pd + ' ';
    //                 }
    //                 final_pd = final_pd + line.price_display + '</pre>';
    //                 line.final_pd = final_pd;
    //             });
    //             var env = {
    //                 widget: self,
    //                 pos: self.pos,
    //                 order: order,
    //                 receipt: receipt,
    //                 paymentlines: self.pos.get_order().get_paymentlines(),
    //             }
    //             var bill_receipt = QWeb.render('OrderReceipt', env);
    //             var Printer = new NetworkDevices();
    //             for (var i = 0; i < printers.length; i++) {
    //                 Printer.print_network_xmlreceipt(self, bill_receipt, printers[i]);
    //             }
    //         }
    //     }
    // });
    // gui.define_screen({name: 'bill', widget: BillScreenWidget});
});