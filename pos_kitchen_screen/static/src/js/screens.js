/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_kitchen_screen.screens', function (require) {

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var ProductScreen = require('point_of_sale.ProductScreen');
    var PaymentScreen = require('point_of_sale.PaymentScreen');
    var SuperPosModel = models.PosModel.prototype;
    var SuperOrder = models.Order.prototype;

  const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const {
        useListener
    } = require('web.custom_hooks');


    models.load_models([{
        model: 'pos.order.line',
        fields: ['product_id', 'order_id', 'qty', 'state'],
        domain: function (self) {
            var today = new Date();
            var validation_date = new Date(today.setDate(today.getDate())).toISOString().split('T')[0];
            if (self.db.pos_screen_data) {
                var pos_categ_ids = []
                _.each(self.db.pos_screen_data, function (data) {
                    pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
                });
                return [
                    ['product_id.pos_categ_id', 'in', pos_categ_ids],
                    ['order_id.date_order', '>=', validation_date],
                    ['order_id.session_id', '=', self.pos_session.name],
                    ['order_id.state', 'not in', ['draft', 'cancel', false]],
                    ['order_id.order_progress', '!=', false]
                ];
            } else
                return [
                    ['order_id.session_id', '=', self.pos_session.name],
                    ['order_id.state', 'not in', ['draft', 'cancel', false]]
                ];
        },
        loaded: function (self, wk_order_lines) {
            console.log("wk_order_lines",wk_order_lines)
            // if (!self.config.module_pos_restaurant) {
            if (!self.config.order_action || (self.config.order_action && self.config.order_action == 'validation')) {
                self.db.pos_all_kitchen_order_lines = wk_order_lines;
                self.db.kitchen_line_by_id = {};
                wk_order_lines.forEach(function (line) {
                    self.db.kitchen_line_by_id[line.id] = line;
                });
            }
        },
    }, {
        model: 'pos.order',
        fields: ['id', 'name', 'date_order', 'order_progress', 'partner_id', 'lines', 'pos_reference', 'kitchen_order_name'],
        domain: function (self) {
            var orders = new Set();
            _.each(self.db.pos_all_kitchen_order_lines, function (line) {
                orders.add(line.order_id[0]);
            });
            console.log("ordersssssssssss",orders)
            var domain_list = [
                ['id', 'in', Array.from(orders)],
                ['kitchen_order_name', '!=', false]
            ];
            return domain_list;
        },
        loaded: function (self, wk_order) {
            console.log("self.config.order_acti11111111on", self.config.order_action)
            if (!self.config.order_action || (self.config.order_action && self.config.order_action == 'validation')) {
                console.log("wrlgn 11111111")
                self.db.pos_all_kitchen_orders = [];
                self.db.kitchen_order_by_id = {};
                self.db.next_order_token = false;
                self.db.orders_in_queue_by_id = {};
                self.db.orders_in_queue = [];
                if (!self.config.order_action || (self.config.order_action && self.config.order_action == 'validation')) {
                wk_order.forEach(function (order) {
                        var order_date = new Date(order['date_order']);
                        var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
                        order['date_order'] = new Date(utc).toLocaleString();
                        self.db.kitchen_order_by_id[order.id] = order;
                        self.db.pos_all_kitchen_orders.push(order.id);
                    });
                    if (self.db.pos_all_kitchen_orders.length)
                        self.db.pos_all_kitchen_orders.reverse();
                    var order_array = self.db.pos_all_kitchen_orders
                    if (self.db.pos_screen_data && self.db.pos_screen_data.queue_order == 'new2old')
                        order_array = self.db.pos_all_kitchen_orders.reverse();
                }
            }
        },
    }, ], {
        'after': 'product.product'
    });

    models.Order = models.Order.extend({
        export_for_printing: function () {
            var self = this
            var receipt = SuperOrder.export_for_printing.call(this)
            if (self.pos.db.next_order_token && self.pos.get_order().validate_order_for_kitchen()) {
                var next_order_token = self.pos.db.next_order_token;
                var new_token = '';
                var token = next_order_token.split("#")[1]
                var new_number = parseInt(token) + 1;
                new_token = "#" + (new_number / 10000).toString().split('.')[1]
                receipt.token_no = new_token;
            }
            return receipt
        },

    })



    models.PosModel = models.PosModel.extend({

        update_token_number: function () {
            var self = this;
            return rpc.query({
                'method': "get_token_number",
                'model': 'pos.order',
            }).then(function (data) {
              console.log('data',data)
                if (data)
                    self.db.next_order_token = data;
                else
                    self.db.next_order_token = '#0000';
            })
        },
        update_kitchen_orders: function () {
            var self = this;
            if (self.db.kitchen_order_by_id)
                var promise = rpc.query({
                    'method': 'update_order_progress',
                    'model': 'pos.order',
                    'args': [Object.keys(self.db.kitchen_order_by_id)]
                }).then(function (data) {
                    if (data) {
                        _.each(data, function (obj) {
                            self.db.kitchen_order_by_id[obj.id.toString()]['order_progress'] = obj.order_progress;
                        })
                    }
                });
            return promise
        },
        _save_to_server: function (orders, options) {
            var self = this;
            return SuperPosModel._save_to_server.call(this, orders, options).then(function (return_dict) {
                if (return_dict) {
                    _.forEach(return_dict, function (data) {
                        if (data.orders != null) {
                            data.orderlines.forEach(function (orderline) {
                                self.db.pos_all_kitchen_order_lines.unshift(orderline);
                                self.db.kitchen_line_by_id[orderline.id] = orderline;
                            });
                            data.orders.forEach(function (order) {
                                var order_date = new Date(order['date_order'])
                                var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
                                order['date_order'] = new Date(utc).toLocaleString();
                                if (self.db.pos_screen_data && self.db.pos_screen_data.queue_order == 'new2old')
                                    self.db.pos_all_kitchen_orders.unshift(order.id);
                                else
                                    self.db.pos_all_kitchen_orders.push(order.id);
                                self.db.kitchen_order_by_id[order.id] = order;
                                if (self.db.kitchen_order_by_id)
                                    self.update_kitchen_orders();
                            });

                            delete data.orders;
                            delete data.orderlines;
                        }
                    })
                }
                return return_dict
            });
        }
    });


    class KitchenScreenWidget extends PosComponent {
        render_list(orders, input_txt) {
            var self = this;
            var new_order_data = [];
            orders = orders.reverse();
            new_order_data = new_order_data.concat(self.env.pos.db.kitchen_order_by_id[orders[i]]);
            if (input_txt != undefined && input_txt != '') {
                var new_order_data = [];
                var search_text = input_txt.toLowerCase()
                for (var i = 0; i < orders.length; i++) {
                    if (self.env.pos.db.kitchen_order_by_id[orders[i]].partner_id == '') {
                        self.env.pos.db.kitchen_order_by_id[orders[i]].partner_id = [0, '-'];
                    }
                    if (self.env.pos.db.kitchen_order_by_id[orders[i]].name) {
                        if (((self.env.pos.db.kitchen_order_by_id[orders[i]].name.toLowerCase()).indexOf(search_text) != -1) || ((self.env.pos.db.kitchen_order_by_id[orders[i]].pos_reference.toLowerCase()).indexOf(search_text) != -1) || (self.env.pos.db.kitchen_order_by_id[orders[i]].kitchen_order_name.indexOf(search_text) != -1) || ((self.env.pos.db.kitchen_order_by_id[orders[i]].order_progress.toLowerCase()).indexOf(search_text) != -1) || ((self.env.pos.db.kitchen_order_by_id[orders[i]].date_order).indexOf(search_text) != -1)) {
                            new_order_data = new_order_data.concat(orders[i]);
                        }
                    } else {
                        if (((self.env.pos.db.kitchen_order_by_id[orders[i]].pos_reference.toLowerCase()).indexOf(search_text) != -1) || (self.env.pos.db.kitchen_order_by_id[orders[i]].kitchen_order_name.indexOf(search_text) != -1) || ((self.env.pos.db.kitchen_order_by_id[orders[i]].order_progress.toLowerCase()).indexOf(search_text) != -1) || ((self.env.pos.db.kitchen_order_by_id[orders[i]].date_order).indexOf(search_text) != -1)) {
                            new_order_data = new_order_data.concat(orders[i]);
                        }
                    }
                }
                orders = new_order_data;
            }
            var count = 0;
            _.each(orders, function (order) {
                self.env.pos.db.kitchen_order_by_id[order].lines.forEach(function (line_id) {
                    if (self.env.pos.db.kitchen_line_by_id[line_id])
                        count++
                });
                self.env.pos.db.kitchen_order_by_id[order].items = count;
                count = 0;
            })
            var contents = $('div.clientlist-screen.screen')[0].querySelector('.wk-kitchen-list-contents');
            contents.innerHTML = "";
            var wk_orders = orders;

            if (wk_orders && wk_orders.length) {
                for (var i = 0, len = Math.min(wk_orders.length, 1000); i < len; i++) {
                    var wk_order = wk_orders[i];
                    var orderline_html = QWeb.render('WkKitchenOrderLine', {
                        env: this.env,
                        order: self.env.pos.db.kitchen_order_by_id[wk_orders[i]],
                        customer_id: self.env.pos.db.kitchen_order_by_id[wk_orders[i]].partner_id[0],
                    });
                    var orderline = document.createElement('tbody');
                    orderline.innerHTML = orderline_html;
                    orderline = orderline.childNodes[1];
                    contents.appendChild(orderline);
                }
            }
        }
        constructor() {
            super(...arguments);
            var self = this;
            setTimeout(function () {
                var orders = self.env.pos.db.pos_all_kitchen_orders;
                self.render_list(orders, undefined);
            }, 150);
        }
        keyup_order_search(event) {
            var orders = this.env.pos.db.pos_all_orders;
            this.render_list(orders, event.target.value);
        }
        clickBack(event) {
            this.showScreen('ProductScreen');
        }
    }
    KitchenScreenWidget.template = 'KitchenScreenWidget';
    Registries.Component.add(KitchenScreenWidget);



    // AllOrdersButton Popup
    class KitchenOrdersButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this;
            if (self.env.pos.db.kitchen_order_by_id) {
                var promise_obj = self.env.pos.update_kitchen_orders();
                promise_obj.then(function (res) {
                    self.showScreen('KitchenScreenWidget', {});
                })
            } else {
                self.showScreen('KitchenScreenWidget', {});
            }
        }
    }
    KitchenOrdersButton.template = 'KitchenOrdersButton';
    ProductScreen.addControlButton({
        component: KitchenOrdersButton,
        condition: function () {
            return true;
        },
    });
    Registries.Component.add(KitchenOrdersButton);




    const PosResPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async validateOrder(isForceValidate) {
                var self = this;
                //console.log('--',self.env.pos.get_order().validate_order_for_kitchen(),(self.env.pos.config.order_action == 'validation' && !self.env.pos.config.order_action) ,(!self.env.pos.get_order().token_no || self.env.pos.get_order().token_no == ''))
                if (self.env.pos.get_order().validate_order_for_kitchen() && (self.env.pos.config.order_action == 'validation' && !self.env.pos.config.order_action) && (!self.pos.get_order().token_no || self.pos.get_order().token_no == '')) {
                    console.log("thissssssssssss11111")
                    const {
                        confirmed
                    } = await this.showPopup('ConfirmPopup', {
                        'title': _t('A Kitchen Order?'),
                        'body': _t('Do you want to send this order to kitchen screen?'),
                    });
                    if (confirmed) {
                        var res = self.env.pos.get_order().add_token_number();
                        res.then(function () {
                            // self._super(force_validation);
                            console.log("wrokinggggggg techniu")
                            SuperPaymentScreenWidget.validate_order.call(self, force_validation);
                        })
                    }
                    if (!confirmed) {
                        super.validateOrder(isForceValidate);
                    }
                } else {
                //  var res = self.env.pos.get_order().add_token_number();
                  super.validateOrder(isForceValidate);
                                  }

            }
        }
    Registries.Component.extend(PaymentScreen, PosResPaymentScreen);


    const PosResProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                var self = this;
                setInterval(self.fetch_updated_orders, 8000, self)
            }
            fetch_updated_orders(self) {
                var order_ref = [];
                _.each(self.env.pos.get('orders').models, function (order) {
                    order_ref.push(order.name);
                });
                rpc.query({
                    method: 'fetch_updated_orders',
                    model: 'pos.order',
                    args: [self.env.pos.config.id, order_ref]
                }).then(function (res) {
                    if (Object.keys(res.orders).length) {
                        self.env.pos.db.recent_notifications.unshift([Object.keys(res.orders)[0], Object.values(res.orders)[0], res.time])
                        var html = QWeb.render('PushNotificationWidget', {
                            'time': res.time,
                            'orders': res.orders
                        });
                        $('.pos').append(html);
                        $('.push_notification > div').animate({
                            'height': '110px'
                        });
                        setTimeout(function () {
                            $('.push_notification').remove();
                            $('.pos').off();
                        }, 4000)
                    }
                    if (res.ref_wise_progress) {
                        _.each(self.env.pos.get('orders').models, function (order) {
                            if (Object.keys(res.ref_wise_progress).indexOf(order.name) != -1)
                                order.order_progress = res.ref_wise_progress[order.name][0];
                            if (Object.keys(res.ref_wise_progress).indexOf(order.name) != -1)
                                order.token_number = res.ref_wise_progress[order.name][1];
                        });
                        // self.env.pos.chrome.widget.order_selector.renderElement();
                    }

                    // $('.pos').on('click','.recent_item',function(ev){
                    //     var token_number = $(ev.currentTarget).find('.push_token_number').text().trim();
                    //     self.env.pos.chrome.gui.show_screen('wk_kitchen_order');
                    //     self.env.pos.chrome.gui.screen_instances.wk_kitchen_order.render_list(self.env.pos.db.pos_all_kitchen_orders,token_number)

                    // })

                })
            }
        }
    Registries.Component.extend(ProductScreen, PosResProductScreen);



    return KitchenOrdersButton;

});
