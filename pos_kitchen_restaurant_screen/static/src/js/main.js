/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_kitchen_restaurant_screen.screens', function (require) {

    var models = require('point_of_sale.models');
    var db = require('point_of_sale.DB');
    var core = require('web.core');
  //  const SubmitOrderButton = require('pos_restaurant.SubmitOrderButton');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    const KitchenOrdersButton = require('pos_kitchen_screen.screens');
    var SuperPosModel = models.PosModel.prototype;
    const Registries = require('point_of_sale.Registries');
    const TicketScreen = require('point_of_sale.TicketScreen');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
	const { useListener } = require('web.custom_hooks');
    var SuperOrder = models.Order.prototype;





    models.load_models([{
        model: 'pos.kitchen.orderline',
        fields: ['product_id', 'order_id', 'qty', 'total_qtys'],
        domain: function (self) {
            var today = new Date();
            var today = new Date(today.setDate(today.getDate())).toISOString();
            var date = today.split('T')
            var validation_date = date[0];

            if (self.db.pos_screen_data) {
                var pos_categ_ids = []
                _.each(self.db.pos_screen_data, function (data) {
                    pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
                });
                console.log("domainnnnnn", [
                    ['product_id.pos_categ_id', 'in', pos_categ_ids],
                    ['order_id.config_id.order_action', '=', 'order_button'],
                    ['order_id.date_order', '>=', validation_date],
                    ['order_id.session_id', '=', self.pos_session.name]
                ])
                return [
                    ['product_id.pos_categ_id', 'in', pos_categ_ids],
                    ['order_id.config_id.order_action', '=', 'order_button'],
                    ['order_id.date_order', '>=', validation_date],
                    ['order_id.session_id', '=', self.pos_session.name]
                ];
            }
        },
        loaded: function (self, wk_order_lines) {
            // if (self.config.module_pos_restaurant) {
                console.log("wke orderlinssssssss",wk_order_lines)
            if (self.config.order_action == 'order_button') {
                    self.db.pos_all_kitchen_order_lines = wk_order_lines;
                self.db.kitchen_line_by_id = {};
                wk_order_lines.forEach(function (line) {
                    self.db.kitchen_line_by_id[line.id] = line;
                });
            }
        },
    }, {
        model: 'pos.kitchen.order',
        fields: ['id', 'name', 'table_id', 'floor_id', 'date_order', 'order_progress', 'partner_id', 'lines', 'pos_reference', 'kitchen_order_name'],
        domain: function (self) {
            var orders = new Set();
            _.each(self.db.pos_all_kitchen_order_lines, function (line) {
                orders.add(line.order_id[0]);
            });
            console.log("ordersssssss restaru",orders)
            var domain_list = [
                ['id', 'in', Array.from(orders)],
                ['kitchen_order_name', '!=', false]
            ];
            return domain_list;
        },
        loaded: function (self, wk_order) {
                console.log("self.config.order_acti22222222",self.config.order_action,wk_order)
                if (self.config.order_action == 'order_button') {
                console.log("wrlgn 2222222222")
                self.db.pos_all_kitchen_orders = [];
                self.db.kitchen_order_by_id = {};
                self.db.next_order_token = false;
                self.db.orders_in_queue_by_id = {};
                self.db.orders_in_queue = [];
                wk_order.forEach(function (order) {
                    var order_date = new Date(order['date_order']);
                    var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
                    order['date_order'] = new Date(utc).toLocaleString();
                    self.db.kitchen_order_by_id[order.id] = order;
                    self.db.pos_all_kitchen_orders.push(order.id);
                });
                if (self.db.pos_all_kitchen_orders.length)
                    self.db.pos_all_kitchen_orders.reverse();
                var order_array = self.db.pos_all_kitchen_orders;
                if (self.db.pos_screen_data && self.db.pos_screen_data.queue_order == 'old2new')
                    self.db.pos_all_kitchen_orders = order_array.reverse();
            }
        },
    }, ], {
        'after': 'product.product'
    });



    const PosResKitchenOrdersButton = (KitchenOrdersButton) =>
        class extends KitchenOrdersButton {

            async onClick() {
                var self = this;
                var promise_obj = null;
                if (self.env.pos.config.module_pos_restaurant && Object.keys(self.env.pos.db.kitchen_order_by_id).length)
                    promise_obj = self.env.pos.update_kitchen_restaurant_orders();
                else
                    promise_obj = self.env.pos.update_kitchen_orders();
                promise_obj.then(function (res) {
                    self.showScreen('KitchenScreenWidget', {env:self.env});
                })
            }
        }
    Registries.Component.extend(KitchenOrdersButton, PosResKitchenOrdersButton);



    var SuperOrderline = models.Orderline.prototype;

    models.Orderline = models.Orderline.extend({

        initialize: function () {
            SuperOrderline.initialize.apply(this, arguments);
            if (typeof this.mp_dirty === 'undefined') {
                this.mp_dirty = this.can_be_shown_to_kitchen() || undefined;
            }
            if (!this.mp_skip) {
                this.mp_skip = false;
            }
        },

        export_as_JSON: function () {
            var self = this;
            var loaded = SuperOrderline.export_as_JSON.call(this);
            loaded.total_qtys = this.get_quantity();
            return loaded;
        },

        can_be_shown_to_kitchen: function () {
            var temp_cat = [];
            _.each(this.pos.db.pos_screen_data, function (data) {
                temp_cat = temp_cat.concat(data.pos_category_ids);
            });
            return this.pos.db.is_product_in_category(temp_cat, this.get_product().id);
        },
        set_quantity: function (quantity) {
            if (quantity !== this.quantity && this.can_be_shown_to_kitchen()) {
                this.mp_dirty = true;
            }
            SuperOrderline.set_quantity.apply(this, arguments);
        },
    });


    db.include({


        is_product_in_category: function (category_ids, product_id) {
            var self = this;
            if (!(category_ids instanceof Array)) {
                category_ids = [category_ids];
            }
            var categs = self.get_product_by_id(product_id).pos_categ_id;
            var count = 0
            var res = false;
            _.each(categs, function (cat) {
                while (cat) {
                    for (var i = 0; i < category_ids.length; i++) {
                        if (cat == category_ids[i]) { // The == is important, ids may be strings
                            count++
                            res = true;
                        }
                    }
                    cat = self.get_category_parent_id(cat);
                }
            })
            return res;
        },
    })

    var SuperPosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        update_kitchen_restaurant_orders: function () {
            var self = this;
            var promise = rpc.query({
                'method': 'update_kitchen_order_progress',
                'model': 'pos.kitchen.order',
                'args': [Object.keys(self.db.kitchen_order_by_id)]
            }).then(function (data) {
                console.log("dataaaaaaaaa",data)
                if (data) {
                    if (data.progress)
                        _.each(data.progress, function (obj) {
                            self.db.kitchen_order_by_id[obj.id.toString()]['order_progress'] = obj.order_progress;
                        })
                    if (data.qtys)
                        _.each(data.qtys, function (obj) {
                            if (Object.keys(self.db.kitchen_line_by_id).indexOf(obj.id.toString()) != -1)
                                self.db.kitchen_line_by_id[obj.id.toString()]['total_qtys'] = obj.total_qtys;
                        })
                }
            });
            return promise
        },

        // delete_current_order: function () {
        //     var self = this;
        //     var order = self.get_order();
        //     SuperPosModel.delete_current_order.call(self)
        //     rpc.query({
        //         'method': 'cancel_kitchen_order',
        //         'model': 'pos.kitchen.order',
        //         'args': [order.name, self.db.pos_screen_data.id]
        //     })

        // },

    });


    const PosResTicketScreen = (TicketScreen) =>
        class extends TicketScreen{
            async deleteOrder(order) {
                super.deleteOrder(order);
                rpc.query({
                    'method': 'cancel_kitchen_order',
                    'model': 'pos.kitchen.order',
                    'args': [order.name, Object.keys(this.env.pos.db.pos_screen_data)]
                })
            }

        }
    Registries.Component.extend(TicketScreen, PosResTicketScreen);

    models.Order = models.Order.extend({




        initialize: function (attributes, options) {
            var self = this;
            self.is_order_sent = false;
            var res = SuperOrder.initialize.call(self, attributes, options);
            return res;
        },


        export_as_JSON: function () {
            var self = this;
            var loaded = SuperOrder.export_as_JSON.call(this);
            if (self.pos.db.pos_screen_data && Object.values(self.pos.db.pos_screen_data)[0] && Object.values(self.pos.db.pos_screen_data)[0].id) {
                loaded.kitchen_config_id = Object.values(self.pos.db.pos_screen_data)[0].id;
            }
            return loaded;
        },

        showChanges: async function () {
            var pos_categ_ids = []
            _.each(this.pos.db.pos_screen_data, function (data) {
                pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
            });
            var changes = this.computeChanges(pos_categ_ids);
            if (changes['new'].length > 0 || changes['cancelled'].length > 0) {
                var receipt = QWeb.render('OrderChangeReceipt', {
                    changes: changes,
                    widget: this
                });
                await printers[i].print_receipt(receipt);
            }
        },
        hasChangesToShow: function () {
            var pos_categ_ids = []
            _.each(this.pos.db.pos_screen_data, function (data) {
                pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
            });
            var changes = this.computeChanges(pos_categ_ids);
            if (changes['new'].length > 0 || changes['cancelled'].length > 0) {
                return true;
            }
            // }
            return false;
        },
    });


    // var SendOrderButton = screens.ActionButtonWidget.extend({
    //     'template': 'SendOrderButton',
    //     button_click: function(){
    //         var self = this;
    //         var pos_categ_ids = []
    //         _.each(this.pos.db.pos_screen_data,function(data){
    //             pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
    //         });
    //         var order = this.pos.get_order();
    //         var changes = order.computeChanges(pos_categ_ids)
    //         if(order.hasChangesToShow())
    //             rpc.query({
    //                     'method':'get_kitchen_order_data',
    //                     'model':'pos.kitchen.order',
    //                     'args':[this.pos.get_order().export_as_JSON(),changes]
    //                 }).then(function(return_dict){
    //                     order.saveChanges();
    //                     order.is_order_sent = true;
    //                     self.add_data_for_updation(return_dict);

    //                 })
    //     },
    //     add_data_for_updation:function(data){
    //         var self = this;
    //         if(data){
    //                 if(data.orders != null){
    //                     data.orderlines.forEach(function(orderline){
    //                         self.pos.db.pos_all_kitchen_order_lines.unshift(orderline);
    //                         self.pos.db.kitchen_line_by_id[orderline.id] = orderline;
    //                     });
    //                     data.orders.forEach(function(order){
    //                         var order_date = new Date(order['date_order'])
    //                         var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
    //                         order['date_order'] = new Date(utc).toLocaleString();
    //                         if (self.pos.db.pos_screen_data && self.pos.db.pos_screen_data.queue_order == 'new2old')
    //                             self.pos.db.pos_all_kitchen_orders.unshift(order.id);
    //                         else
    //                             self.pos.db.pos_all_kitchen_orders.push(order.id);
    //                         self.pos.db.kitchen_order_by_id[order.id] = order;
    //                         if(self.pos.get_order() && self.pos.get_order().name == order.pos_reference)
    //                             self.pos.get_order().token_no = self.pos.get_order().token_no;
    //                         if(Object.keys(self.pos.db.kitchen_order_by_id).length)
    //                             self.pos.update_kitchen_restaurant_orders();
    //                     });

    //                     delete data.orders;
    //                     delete data.orderlines;
    //                 }
    //         }

    //     },
    // });

    // screens.define_action_button({
    //     'name': 'send_order',
    //     'widget': SendOrderButton,
    //     'condition': function() {
    //         return this.pos.config.order_action == 'order_button';
    //     },
    // });


    // SendOrderButton
	class SendOrderButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
            this._currentOrder = this.env.pos.get_order();
            this._currentOrder.orderlines.on('change', this.render, this);
            this.env.pos.on('change:selectedOrder', this._updateCurrentOrder, this);
        }
        willUnmount() {
            this._currentOrder.orderlines.off('change', null, this);
            this.env.pos.off('change:selectedOrder', null, this);
        }
        async onClick() {
            var self = this;
            var pos_categ_ids = []
            _.each(this.env.pos.db.pos_screen_data,function(data){
                pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
            });
            var order = this.env.pos.get_order();
            var changes = order.computeChanges(pos_categ_ids)
            console.log("thissss")

            if(order.hasChangesToShow()){

                rpc.query({
                        'method':'get_kitchen_order_data',
                        'model':'pos.kitchen.order',
                        'args':[this.env.pos.get_order().export_as_JSON(),changes]
                    }).then(function(return_dict){
                        order.saveChanges();
                        order.is_order_sent = true;
                        self.add_data_for_updation(return_dict);

                    })

                }
        }
        add_data_for_updation(data) {
            var self = this;
            if (data) {
                if (data.orders != null) {
                    data.orderlines.forEach(function (orderline) {
                        self.env.pos.db.pos_all_kitchen_order_lines.unshift(orderline);
                        self.env.pos.db.kitchen_line_by_id[orderline.id] = orderline;
                    });
                    data.orders.forEach(function (order) {
                        var order_date = new Date(order['date_order'])
                        var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
                        order['date_order'] = new Date(utc).toLocaleString();
                        if (self.env.pos.db.pos_screen_data && self.env.pos.db.pos_screen_data.queue_order == 'new2old')
                            self.env.pos.db.pos_all_kitchen_orders.unshift(order.id);
                        else
                            self.env.pos.db.pos_all_kitchen_orders.push(order.id);
                        self.env.pos.db.kitchen_order_by_id[order.id] = order;
                        if (Object.keys(self.env.pos.db.kitchen_order_by_id).length)
                            self.env.pos.update_kitchen_restaurant_orders();
                    });

                    delete data.orders;
                    delete data.orderlines;
                }
            }

        }
        _updateCurrentOrder(pos, newSelectedOrder) {
            this._currentOrder.orderlines.off('change', null, this);
            if (newSelectedOrder) {
                this._currentOrder = newSelectedOrder;
                this._currentOrder.orderlines.on('change', this.render, this);
            }
        }
        get addClasses() {
            if (!this._currentOrder) return {};
            var changes = this._currentOrder.hasChangesToShow();
            var skipped = changes ? false : this._currentOrder.hasSkippedChanges();
            console.log("changessssss",changes)
            return {
                highlight: changes,
                altlight: skipped,
            };
        }
    }
    SendOrderButton.template = 'SendOrderButton';
    ProductScreen.addControlButton({ component: SendOrderButton, condition: function() {
        if(this.env.pos.config.order_action == 'order_button')
        return true;
    },});
    Registries.Component.add(SendOrderButton);




    // const PosResSubmitOrderButton = (SubmitOrderButton) =>
    //     class extends SubmitOrderButton {
    //         get addedClasses() {
    //             if (!this._currentOrder) return {};
    //             var changes = false;
    //             var skipped = false;
    //             if (this.env.pos.config.type_of_order_action == 'show_on_kitchen') {
    //                 changes = this._currentOrder.hasChangesToShow();
    //                 skipped = changes ? false : this._currentOrder.hasSkippedChanges();
    //             } else if (this.env.pos.config.type_of_order_action == 'both') {
    //                 changes = this._currentOrder.hasChangesToShow() || this._currentOrder.hasChangesToPrint();
    //                 skipped = changes ? false : this._currentOrder.hasSkippedChanges();
    //             } else {
    //                 changes = this._currentOrder.hasChangesToPrint();
    //                 skipped = changes ? false : this._currentOrder.hasSkippedChanges();
    //             }
    //             return {
    //                 highlight: changes,
    //                 altlight: skipped,
    //             };
    //         }
    //         async onClick() {
    //             var self = this;
    //             var pos_categ_ids = []
    //             if (this.env.pos.db.pos_screen_data) {
    //                 _.each(this.env.pos.db.pos_screen_data, function (data) {
    //                     pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
    //                 });
    //                 if (this.env.pos.config.type_of_order_action == 'print') {
    //                     this._super()
    //                 } else if (this.env.pos.config.type_of_order_action == 'both') {
    //                     this._super();
    //                     var order = this.env.pos.get_order();
    //                     var changes = order.computeChanges(pos_categ_ids)
    //                     if (order.hasChangesToShow())
    //                         rpc.query({
    //                             'method': 'get_kitchen_order_data',
    //                             'model': 'pos.kitchen.order',
    //                             'args': [self.env.pos.get_order().export_as_JSON(), changes]
    //                         }).then(function (return_dict) {
    //                             order.saveChanges();
    //                             order.is_order_sent = true;
    //                             self.add_data_for_updation(return_dict);
    //                         })
    //                 } else {
    //                     var order = this.env.pos.get_order();
    //                     var changes = order.computeChanges(pos_categ_ids)
    //                     if (order.hasChangesToShow())
    //                         rpc.query({
    //                             'method': 'get_kitchen_order_data',
    //                             'model': 'pos.kitchen.order',
    //                             'args': [this.env.pos.get_order().export_as_JSON(), changes]
    //                         }).then(function (return_dict) {
    //                             order.saveChanges();
    //                             order.is_order_sent = true;
    //                             self.add_data_for_updation(return_dict);

    //                         })
    //                 }
    //             } else {
    //                 this.showPopup('ErrorPopup', {
    //                     title: this.env._t('No Kitchen Configuration!!'),
    //                     body: this.env._t('No kitchen configuration found!!.'),
    //                 });
    //             }
    //         }
    //         add_data_for_updation(data) {
    //             var self = this;
    //             if (data) {
    //                 if (data.orders != null) {
    //                     data.orderlines.forEach(function (orderline) {
    //                         self.env.pos.db.pos_all_kitchen_order_lines.unshift(orderline);
    //                         self.env.pos.db.kitchen_line_by_id[orderline.id] = orderline;
    //                     });
    //                     data.orders.forEach(function (order) {
    //                         var order_date = new Date(order['date_order'])
    //                         var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
    //                         order['date_order'] = new Date(utc).toLocaleString();
    //                         if (self.env.pos.db.pos_screen_data && self.env.pos.db.pos_screen_data.queue_order == 'new2old')
    //                             self.env.pos.db.pos_all_kitchen_orders.unshift(order.id);
    //                         else
    //                             self.env.pos.db.pos_all_kitchen_orders.push(order.id);
    //                         self.env.pos.db.kitchen_order_by_id[order.id] = order;
    //                         if (Object.keys(self.env.pos.db.kitchen_order_by_id).length)
    //                             self.env.pos.update_kitchen_restaurant_orders();
    //                     });

    //                     delete data.orders;f
    //                     delete data.orderlines;
    //                 }
    //             }

    //         }
    //     }
    // Registries.Component.extend(SubmitOrderButton, PosResSubmitOrderButton);


});
