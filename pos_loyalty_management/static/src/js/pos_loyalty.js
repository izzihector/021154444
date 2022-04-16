/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_loyalty_management.pos_loyalty', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
	var rpc = require('web.rpc')
    var core = require('web.core');
    var utils = require('web.utils');
    var QWeb = core.qweb;
    var _t = core._t;
    const OrderWidget = require('point_of_sale.OrderWidget');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    models.load_fields('res.partner', 'wk_loyalty_points');
    models.load_fields('product.product', 'wk_point_for_loyalty');

    models.load_models([{
        model: 'loyalty.management',
        fields: ['loyalty_base', 'points', 'purchase', 'minimum_purchase', 'message', 'minimum_points'],
        domain: function(self) { return [['config_active', '=', true]]; },
        loaded: function(self, result) {
            self.db.loyality_product_id = null;
            if (result.length) {
                self.set('loyalty_base', result[0].loyalty_base);
                self.set('loyalty_points', result[0].points);
                self.set('loyalty_purchase', result[0].purchase);
                self.set('loyalty_min_purchase', result[0].minimum_purchase);
                self.set('loyalty_message', result[0].message);
                self.set('loyalty_min_points', result[0].minimum_points)||0;
            }
        },}], { 'after': 'product.product' });


    var _super = models.Order;
    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            this.set({
                redeemTaken: false,
                totalEarnedPoint: 0,
                voucherProductId: 0,
                discount_offer: 0,
                total_points: 0,
                debit_points: 0,
            });
        _super.prototype.initialize.apply(this, arguments);
        },
        remove_orderline: function(line) {
            var product_id = line.product.id;
            var currentOrder = this.pos.get_order();
            if(currentOrder){
                if (product_id == this.get('voucherProductId')) {
                    currentOrder.set_client_loyal_points(currentOrder.get_client_loyal_points() + currentOrder.get('debit_points'));
                    this.set('redeemTaken', false);
                    this.set('debit_points', 0);
                    this.set('discount_offer', 0);
                }
            }
            _super.prototype.remove_orderline.apply(this, arguments);
        },
        get_client_loyal_points: function() {
            return this.get('total_points');
        },
        set_client_loyal_points: function(points) {
            for(var i in this.pos.get_order_list()){
                var order = this.pos.get_order_list()[i];
                if((order.get_client() ? order.get_client().id:-1)==this.get_client().id){
                        order.set('total_points', points);
                    }
                }
                this.save_to_db();
        },
        // This is Updated function
        get_loyalty_points: function() {
            var orderLines = this.get_orderlines();
            var total_loyalty = 0;

            var loyalty_base = this.pos.get('loyalty_base');

            if (loyalty_base == 'category') {
                for (var i = 0; i < orderLines.length; i++) {
                    var line = orderLines[i];
                    if (line.product.wk_point_for_loyalty > 0) {
                        total_loyalty += round_pr(line.get_quantity() * line.product.wk_point_for_loyalty, 1);
                    }
                }
            } else {
                var currentOrder = this.pos.get_order();
                var tpointsvalue = currentOrder.get_total_with_tax();
                var points = this.pos.get('loyalty_points');
                var purchase = this.pos.get('loyalty_purchase');
                var minimum_purchase = this.pos.get('loyalty_min_purchase');
                var client = currentOrder.get_client();
                if (client && points && purchase) {
                    if (tpointsvalue >= minimum_purchase) {
                        total_loyalty = this.calculate_loyalty_points(tpointsvalue, purchase, points);
                    }

                }
            }
            return total_loyalty;
        },
        calculate_loyalty_points: function(total, purchase, points) {
            return parseInt(total / purchase) * points;
        },
        init_from_JSON: function(json) {
            this.set('total_points',json.total_points);
            this.set('totalEarnedPoint', json.tpoints);
            this.set('redeemTaken', json.redeemTaken);
            this.set('debit_points', json.debit_points);
            this.set('voucherProductId', json.voucherProductId);


            _super.prototype.init_from_JSON.call(this, json);
        },
        export_for_printing: function() {
            var currentOrder = this.pos.get_order();
            var json = _super.prototype.export_for_printing.apply(this, arguments);
            json.wk_loyalty_points = this.get_loyalty_points();
            json.tpoints = currentOrder.get('totalEarnedPoint');
            json.redeemTaken = currentOrder.get('redeemTaken');
            return json;
        },
        export_as_JSON: function() {
            self = this;
            var currentOrder = self.pos.get_order();
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            var client_points = 0;
            if (currentOrder != undefined) {
                var client = currentOrder.get_client();
                if (client) client_points = (self.get('redeemTaken')==true ?client.wk_loyalty_points:0) -(self.get('redeemTaken')==true ?self.get('debit_points'):0) + self.get_loyalty_points();
                json.wk_loyalty_points = (client_points || this.get_loyalty_points()) || 0;
                json.tpoints = currentOrder.get('totalEarnedPoint');
            }
            json.total_points = self.get('total_points');
            json.redeemTaken = self.get('redeemTaken');
            json.debit_points = self.get('debit_points');
            json.voucherProductId = self.get('voucherProductId');
            return json;
        },

        set_client: function(client) {
			var self = this;
            if(self.get('redeemTaken')){
                self.orderlines.models.forEach(function(line){
                    if (line.product.id == self.pos.db.loyality_product_id){
                        self.remove_orderline(line);
                    }
                });
            }
            if(client && this.pos.get_order()){
                var loyal_points = 0;
                var count = 0;
                for(var i = 0 ; i < self.pos.get_order_list().length; i++){
                    var order = self.pos.get_order_list()[i];
                    if((order.get_client() ? order.get_client().id:-1)==client.id){
                            loyal_points = order.get('total_points') || loyal_points;
                            count++;
                        }
                    }
                if (count || loyal_points ){
                    self.set('total_points',loyal_points);
                }
                else{
                    self.set('total_points',client.wk_loyalty_points);
                }
            }
            _super.prototype.set_client.call(this, client);
        },
    });

    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen').prototype;



    const PosOrderWidget = (OrderWidget) =>
        class extends OrderWidget {
            _updateSummary(){
                // this._super();
                super._updateSummary();
                self = this;
                var order = this.env.pos.get_order();
                var client = order.get_client();
                var $loypoints = $(this.el).find('.summary .loyalty-points');
                if(self.env.pos.db && !self.env.pos.db.loyality_product_id )
                    self.get_loyalty_product_id();
                if (client) {
                    var points = order.get_loyalty_points();
                    var points_total = order.get_client_loyal_points() + points;
                    var points_str = this.env.pos.format_pr(points, 1);
                    var total_str = this.env.pos.format_pr(points_total, 1);
                    if (points && points > 0) {

                        points_str = '+' + points_str;
                    }
                    $loypoints.replaceWith($(QWeb.render('LoyaltyPoints', {
                        widget: this,
                        totalpoints: total_str,
                        wonpoints: points_str
                    })));
                    $loypoints = $(this.el).find('.summary .loyalty-points');
                    $loypoints.removeClass('oe_hidden');
                } else {
                    $loypoints.empty();
                    $loypoints.addClass('oe_hidden');
                }
            }
            get_loyalty_product_id(){
                var self = this;
                var done = new $.Deferred
                rpc.query({
                    model:'loyalty.management',
                    method:'get_loyalty_product',
                    args:[]
                })
                .catch(function(unused, event) {
                    msg = _t('Failed to fetch Loyalty Product, Configure Loyalty Rules!!!');
                    self.loyalty_error_alert(msg);
                }).then(function(product_id) {
                    if (product_id){
                        self.env.pos.db.loyality_product_id = product_id;
                    }
                });
            }
        }

        Registries.Component.extend(OrderWidget, PosOrderWidget);
    
        return OrderWidget;
    });
