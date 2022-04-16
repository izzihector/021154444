odoo.define('pos_promotional_scheme.chrome_extended', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {
        useListener
    } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var data, prod, remained;
    class CheckSchemeWidget extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async apply_scheme() {
            var self = this;
            console.log('-this--this-------------')
            console.log(self)
            var pos_obj = self.env.pos;
            console.log('----------------------')
            console.log(pos_obj)
            var new_q = new Array();
            var get_product_id_list = new Array();
            var order = pos_obj.get('selectedOrder');
            console.log(order)

            var order_orderlines = order.get_orderlines();
            var orderlines = new Array();
            var orderlines_unit_price = new Array();
            var schemes = pos_obj.scheme; //Getting all available schemes
            var available_on = pos_obj.available_on_list; //Getting records from loyalty.available_on
            var get_product_orderlines = order.get_orderLineCollection_obj();
            var qty;
            var scheme_discount;
            _.each(order_orderlines, function(orderline) {

                orderlines.push(orderline);
                orderlines_unit_price.push(orderline);
            });

            for (var s = 0; s < schemes.length; s++) {
                var avail = schemes[s].available_on;
                var scheme_basis = schemes[s].scheme_basis;
                if (schemes[s].scheme_type == 'buy_x_get_y') {
                    if (scheme_basis == 'on_diff_prod') {
                        var neworderLines = order.get_orderLineCollection_obj();
                        var modified_orderlines = order.get_orderLineCollection_obj();
                        var prod_list = new Array();
                        for (var n = 0; n < avail.length; n++) {
                            for (var p = 0; p < this.get_available_on_product_list(avail[n]).length; p++) {
                                prod_list.push(this.get_available_on_product_list(avail[n])[p])
                            }
                        }
                        console.log("prod_list::::", prod_list);
                        //First line's available products
                        qty = 0;
                        for (var p = 0; p < prod_list.length; p++) {
                            //Check if product is available in orderline
                            for (var o = 0; o < orderlines.length; o++) {
                                if (prod_list[p] == orderlines[o].get_product().id) {
                                    neworderLines.add(orderlines[o]);
                                    qty += orderlines[o].quantity;
                                    order.remove_orderline(orderlines[o]);
                                }
                            }
                        }

                        if (qty >= schemes[s].buy_a_qty) {
                            var getqty = 0;
                            var orderline_data_new = new Array();
                            var get_product_list = schemes[s].scheme_product;
                            scheme_discount = schemes[s].discount;
                            for (var p = 0; p < get_product_list.length; p++) {
                                var plist = this.get_available_on_product_list(get_product_list[p]);
                                for (var pl = 0; pl < plist.length; pl++) {
                                    for (var o = 0; o < orderlines.length; o++) {
                                        if (plist[pl] == orderlines[o].get_product().id) {
                                            get_product_id_list.push(orderlines[o].get_product().id)
                                            getqty += orderlines[o].quantity;
                                            get_product_orderlines.add(orderlines[o]);
                                            orderline_data_new.push({
                                                key: orderlines[o].get_product().id,
                                                value: orderlines[o].quantity
                                            });
                                            order.remove_orderline(orderlines[o]);
                                        }
                                    }
                                }

                            }
                            if (getqty >= schemes[s].get_a_qty) {
                                var lines = new Array();
                                neworderLines.each(function(orderline) {
                                    lines.push(orderline);
                                });
                                for (var m = 0; m < lines.length; m++) {
                                    modified_orderlines.add(lines[m]);
                                }
                                var temp_orderline_data_new = new Array();
                                for (var x in orderline_data_new) {
                                    if (temp_orderline_data_new.length == 0) {
                                        temp_orderline_data_new.push({
                                            key: orderline_data_new[x].key,
                                            value: orderline_data_new[x].value
                                        });
                                    } else {
                                        var flag = false;
                                        for (var y in temp_orderline_data_new) {
                                            if (temp_orderline_data_new[y].key == orderline_data_new[x].key) {
                                                temp_orderline_data_new[y].value += orderline_data_new[x].value;
                                                flag = true;
                                            }
                                        }
                                        if (flag == false) {
                                            temp_orderline_data_new.push({
                                                key: orderline_data_new[x].key,
                                                value: orderline_data_new[x].value
                                            });
                                        }
                                    }
                                }
                                //display same product merged orderlies
                                var getlines = new Array();
                                for (var item in temp_orderline_data_new) {
                                    getlines.push(temp_orderline_data_new[item])
                                }
                                var gq = (Math.floor(qty / schemes[s].buy_a_qty) * schemes[s].get_a_qty) * (getlines.length);
                                for (var v = 0; v < getlines.length; v++) {
                                    if (getlines[v].value >= qty) {
                                        var line_product = this.env.pos.db.get_product_by_id(getlines[v].key);
                                        order.add_product(line_product, {
                                            quantity: qty,
                                            discount: schemes[s].discount
                                        });
                                        var sq = (getlines[v].value - qty)
                                        if (sq > 0) {
                                            //adding remained product with full price
                                            var line_product = this.env.pos.db.get_product_by_id(getlines[v].key);
                                            order.add_product(line_product, {
                                                quantity: sq
                                            });
                                        }
                                    } else if (getlines[v].value < qty) {
                                        var line_product = this.env.pos.db.get_product_by_id(getlines[v].key);
                                        order.add_product(line_product, {
                                            quantity: getlines[v].value,
                                            discount: schemes[s].discount
                                        });
                                    }
                                } //getlines for loop
                            } else {
                                //add buy product orderline as it is
                                neworderLines.each(function(orderline) {
                                    var line_product = pos_obj.db.get_product_by_id(orderline.get_product().id);
                                    order.add_product(line_product, {
                                        quantity: orderline.quantity
                                    });

                                });
                                //add get product orderline as it is
                                get_product_orderlines.each(function(orderline) {
                                    console.log(orderline.get_product().id);
                                    var line_product = pos_obj.db.get_product_by_id(orderline.get_product().id);
                                    order.add_product(line_product, {
                                        quantity: orderline.quantity
                                    });
                                });
                            }
                            qty = 0;
                            getqty = 0;
                        } else {
                            //add original orderline as it is
                            neworderLines.each(function(orderline) {
                                var line_product = pos_obj.db.get_product_by_id(orderline.get_product().id);
                                order.add_product(line_product, {
                                    quantity: orderline.quantity
                                });
                            });
                        }
                    } //end of on_diff_product
                    else //on same product
                    {
                        for (var n = 0; n < avail.length; n++) {
                            var neworderLines = order.get_orderLineCollection_obj();
                            var prod_list = this.get_available_on_product_list(avail[n]);
                            //First line's available products
                            var bqty = 0;
                            var gqty = 0;
                            var lin = new Array();
                            var buy_id = new Array();
                            for (var p = 0; p < prod_list.length; p++) {
                                //Check if product is available in orderline
                                for (var o = 0; o < orderlines.length; o++) {
                                    if (prod_list[p] == orderlines[o].get_product().id) {
                                        bqty += orderlines[o].quantity;
                                        neworderLines.add(orderlines[o]);
                                        lin.push(orderlines[o].quantity)
                                        order.remove_orderline(orderlines[o]);
                                        buy_id.push(orderlines[o].get_product().id)
                                    }
                                }
                            }
                            if (bqty >= schemes[s].buy_a_qty) {
                                var getqty = 0;
                                var get_product_list = schemes[s].available_on;
                                var scheme_bqty = schemes[s].buy_a_qty;
                                var scheme_gqty = schemes[s].get_a_qty;
                                var original_orderline_array = new Array()
                                var j = 1;
                                neworderLines.each(function(orderline) {
                                    for (i = 0; i < orderline.quantity; i++) {
                                        original_orderline_array.push({
                                            id: j,
                                            new_product_id: orderline.get_product().id,
                                            price: orderline.price,
                                            qty: 1
                                        });
                                        j++;
                                    }
                                });
                                original_orderline_array.sort(function(a, b) {
                                    return (b.price) - (a.price)
                                });
                                var summed_bqty = 0;
                                var summed_gqty = 0;
                                var cnt = 0;
                                if (original_orderline_array.length > 0) {
                                    for (var product = 0; product < original_orderline_array.length; product++) {
                                        summed_bqty += original_orderline_array[product].qty
                                        cnt += original_orderline_array[product].qty
                                        var line_buy_product = this.env.pos.db.get_product_by_id(original_orderline_array[product].new_product_id);
                                        order.add_product(line_buy_product, {
                                            quantity: 1,
                                            discount: 0
                                        });
                                        if (summed_bqty == scheme_bqty) {
                                            for (i = (original_orderline_array.length - 1); i >= cnt; i--) {
                                                summed_gqty += original_orderline_array[i].qty;
                                                var line_get_product = this.env.pos.db.get_product_by_id(original_orderline_array[i].new_product_id);
                                                order.add_product(line_get_product, {
                                                    quantity: 1,
                                                    discount: schemes[s].discount,
                                                    merge: false
                                                });
                                                original_orderline_array.pop()
                                                if (summed_gqty == scheme_gqty) {
                                                    summed_bqty = 0;
                                                    summed_gqty = 0
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                }
                            } else {
                                var norderlines2 = new Array();
                                neworderLines.each(function(orderline) {
                                    norderlines2.push(orderline);
                                });
                                for (var i = 0; i < norderlines2.length; i++) {
                                    order.add_orderline(norderlines2[i]);
                                }
                            }
                        } //avail loop
                    } //same product loop

                } //end of scheme buy_x get_y


                ///////////////////////////////////////////////////////////////////////////////
                // Unit Price Discount Amount
                ////////////////////////////////////////////////////////////////////////////////
                else if (schemes[s].scheme_type == 'unit_price_disc_amt') {
                    var scheme_qty = schemes[s].qty_disc;
                    var remain_arr = new Array();
                    var prod_list = new Array();
                    for (var n = 0; n < avail.length; n++) {
                        for (var p = 0; p < this.get_available_on_product_list(avail[n]).length; p++) {
                            prod_list.push(this.get_available_on_product_list(avail[n])[p]);
                        }
                    }
                    //First line's available products
                    var qty = 0;
                    var scheme_prod_list = new Array()
                    var orderline_prod_ids = new Array();
                    var id_qty_dict = []; // create an empty array
                    var orderline_data = [];
                    var temp_orderline_data = [];
                    var same_product_exists_flag = false;
                    var flag = false;
                    var count = 0;
                    for (var p = 0; p < prod_list.length; p++) {
                        //Check if product is available in orderline
                        for (var o = 0; o < orderlines.length; o++) {
                            if (prod_list[p] == orderlines[o].get_product().id) {
                                orderline_data.push({
                                    key: orderlines[o].get_product().id,
                                    value: orderlines[o].quantity
                                });
                                order.remove_orderline(orderlines[o]);
                            }
                        }
                    }

                    //MERGE REPEATED PRODUCTS QUANTITY
                    for (var x in orderline_data) {
                        if (temp_orderline_data.length == 0) {
                            temp_orderline_data.push({
                                key: orderline_data[x].key,
                                value: orderline_data[x].value
                            });
                        } else {
                            var flag = false;
                            for (y in temp_orderline_data) {
                                if (temp_orderline_data[y].key == orderline_data[x].key) {
                                    temp_orderline_data[y].value += orderline_data[x].value;
                                    flag = true;
                                }
                            }
                            if (flag == false) {
                                temp_orderline_data.push({
                                    key: orderline_data[x].key,
                                    value: orderline_data[x].value
                                });
                            }
                        }
                    }
                    //DISPLAY MERGED ARRAY
                    for (var item in temp_orderline_data) {
                        scheme_prod_list.push(temp_orderline_data[item])
                    }
                    var scheme_qty = schemes[s].qty_disc;
                    var qty_arranged_dict = new Array();
                    var qty = [];
                    var qty_on = this.env.pos.qty_disc; //Getting records from loyalty.available_on

                    //CREATE DICT OF DISC_QTY ID AND QTY
                    for (var x = 0; x < scheme_qty.length; x++) {
                        for (var l = 0; l < qty_on.length; l++) {
                            if (scheme_qty[x] == qty_on[l].id) {
                                qty_arranged_dict.push({
                                    key: scheme_qty[x],
                                    value: qty_on[l].qty
                                });
                            }
                        }
                    }

                    //SORT THE DICT TO GET HIGHEST QTY
                    qty_arranged_dict.sort(function(a, b) {
                        return (b.value) - (a.value)
                    });
                    var product_discounted = false;
                    for (var product = 0; product < scheme_prod_list.length; product++) {
                        var qt = this.get_scheme_qty(scheme_qty[qty]);
                        for (var item in qty_arranged_dict) {
                            if (scheme_prod_list[product].value >= qty_arranged_dict[item].value) {
                                var divide_qty = Math.floor(scheme_prod_list[product].value / qty_arranged_dict[item].value)
                                var qty_obtained = divide_qty * qty_arranged_dict[item].value
                                var qty_remained = scheme_prod_list[product].value - qty_obtained
                                var scheme_qty_discount = this.get_scheme_discount(qty_arranged_dict[item].key);
                                var prod_obj = this.env.pos.product_obj;
                                for (prd in scheme_prod_list) {
                                    for (prod in prod_obj) {
                                        if (prod_obj[prod].id == scheme_prod_list[prd].key) {
                                            product_list_price = prod_obj[prod].list_price
                                            product_extra_price = prod_obj[prod].price_extra
                                            product_price = (product_list_price + product_extra_price)
                                        }
                                    }
                                }
                                var line_product = this.env.pos.db.get_product_by_id(scheme_prod_list[product].key);
                                order.add_product(line_product, {
                                    price: scheme_qty_discount,
                                    quantity: qty_obtained
                                });
                                remained = qty_remained;
                                var least_qty = qty_arranged_dict[qty_arranged_dict.length - 1].value
                                while (remained >= least_qty) {
                                    for (dict_item in qty_arranged_dict) {
                                        var sch_qty_disc = this.get_scheme_discount(qty_arranged_dict[dict_item].key);
                                        if (qty_arranged_dict[dict_item].value <= remained) {
                                            var line_product = this.env.pos.db.get_product_by_id(scheme_prod_list[product].key);
                                            order.add_product(line_product, {
                                                price: sch_qty_disc,
                                                quantity: qty_arranged_dict[dict_item].value
                                            });
                                            remained -= qty_arranged_dict[dict_item].value
                                        }
                                    }
                                }
                                if (remained > 0) {
                                    var line_product = this.env.pos.db.get_product_by_id(scheme_prod_list[product].key);
                                    order.add_product(line_product, {
                                        price: product_price,
                                        quantity: remained
                                    });
                                }
                                product_discounted = true;
                                break;
                            }
                        } //END OF qty_arranged_dict
                        if (product_discounted == false) {
                            var line_product = this.env.pos.db.get_product_by_id(scheme_prod_list[product].key);
                            order.add_product(line_product, {
                                quantity: scheme_prod_list[product].value
                            });
                        }
                    } //END OF scheme_prod_list
                } //END OF unit_price_disc_ammount scheme

                ////////////////////////////////////////////////////////////////////////////
                //            unit price discount percent
                ////////////////////////////////////////////////////////////////////////////
                else if (schemes[s].scheme_type == 'unit_price_disc_percent') {
                    var prod_list = new Array();
                    var scheme_qty = schemes[s].qty_disc;
                    var remain_arr = new Array()

                    for (var n = 0; n < avail.length; n++) {
                        for (var p = 0; p < this.get_available_on_product_list(avail[n]).length; p++) {
                            prod_list.push(this.get_available_on_product_list(avail[n])[p]);
                        }
                    }
                    //First line's available products
                    qty = 0;
                    var scheme_prod_list = new Array();
                    var orderline_prod_ids = new Array();
                    var id_qty_dict = []; // create an empty array
                    var orderline_data = [];
                    var temp_orderline_data = [];
                    var product_ids = [];
                    var same_product_exists_flag = false;
                    var flag = false;
                    var count = 0;
                    for (var p = 0; p < prod_list.length; p++) {
                        //Check if product is available in orderline
                        for (var o = 0; o < orderlines.length; o++) {
                            if (prod_list[p] == orderlines[o].get_product().id) {

                                orderline_data.push({
                                    key: orderlines[o].get_product().id,
                                    value: orderlines[o].quantity
                                });
                                product_ids.push({
                                    key: orderlines[o].get_product().id,
                                    value: orderlines[o].price
                                });
                                order.remove_orderline(orderlines[o]);
                            }
                        }
                    }

                    //MERGE REPEATED PRODUCTS QUANTITY
                    for (x in orderline_data) {
                        if (temp_orderline_data.length == 0) {
                            temp_orderline_data.push({
                                key: orderline_data[x].key,
                                value: orderline_data[x].value
                            });
                        } else {
                            var flag = false
                            for (y in temp_orderline_data) {


                                if (temp_orderline_data[y].key == orderline_data[x].key) {
                                    temp_orderline_data[y].value += orderline_data[x].value
                                    flag = true
                                }
                            }
                            if (flag == false) {
                                temp_orderline_data.push({
                                    key: orderline_data[x].key,
                                    value: orderline_data[x].value
                                });
                            }
                        }
                    }

                    //DISPLAY MERGED ARRAY
                    for (data in temp_orderline_data) {

                    }
                    //}//end of available loop
                    for (item in temp_orderline_data) {
                        scheme_prod_list.push(temp_orderline_data[item])
                    }

                    for (prod in scheme_prod_list) {

                    }

                    var scheme_qty = schemes[s].qty_disc;
                    var qty_arranged_dict = new Array()
                    var qty = []
                    var qty_on = this.env.pos.qty_disc; //Getting records from loyalty.available_on

                    //CREATE DICT OF DISC_QTY ID AND QTY
                    for (var x = 0; x < scheme_qty.length; x++) {
                        for (var l = 0; l < qty_on.length; l++) {
                            if (scheme_qty[x] == qty_on[l].id) {
                                qty_arranged_dict.push({
                                    key: scheme_qty[x],
                                    value: qty_on[l].qty
                                });
                            }
                        }
                    }

                    //SORT THE DICT TO GET HIGHEST QTY
                    qty_arranged_dict.sort(function(a, b) {
                        return (b.value) - (a.value)
                    })


                    for (x in qty_arranged_dict) {

                    }

                    var product_discounted = false
                    for (var product = 0; product < scheme_prod_list.length; product++) {
                        var qt = this.get_scheme_qty(scheme_qty[qty]);
                        var product_price;
                        for (item in qty_arranged_dict) {
                            if (scheme_prod_list[product].value >= qty_arranged_dict[item].value) {
                                var divide_qty = Math.floor(scheme_prod_list[product].value / qty_arranged_dict[item].value)
                                var qty_obtained = divide_qty * qty_arranged_dict[item].value
                                var qty_remained = scheme_prod_list[product].value - qty_obtained
                                var scheme_qty_discount = this.get_scheme_discount(qty_arranged_dict[item].key);
                                var prod_obj = this.env.pos.product_obj;

                                //GET PRODUCT PRICE(LIST_PRICE + PRICE_EXTRA)
                                for (prd in scheme_prod_list) {
                                    for (prod in prod_obj) {
                                        if (prod_obj[prod].id == scheme_prod_list[prd].key) {
                                            product_list_price = prod_obj[prod].list_price
                                            product_extra_price = prod_obj[prod].price_extra
                                            product_price = (product_list_price + product_extra_price)
                                        }
                                    }
                                }

                                //COMPUTE DISCOUNT
                                var compute_discount = (product_price * (scheme_qty_discount / 100))
                                var final_discount = (product_price - compute_discount)
                                var line_product = this.env.pos.db.get_product_by_id(scheme_prod_list[product].key);
                                order.add_product(line_product, {
                                    discount: scheme_qty_discount,
                                    quantity: qty_obtained
                                });


                                remained = qty_remained;
                                var least_qty = qty_arranged_dict[qty_arranged_dict.length - 1].value
                                while (remained >= least_qty) {
                                    for (dict_item in qty_arranged_dict) {
                                        var sch_qty_disc = this.get_scheme_discount(qty_arranged_dict[dict_item].key);
                                        var compute_discount = (product_price * (sch_qty_disc / 100))
                                        var final_discount = (product_price - compute_discount)
                                        if (qty_arranged_dict[dict_item].value <= remained) {
                                            var line_product = this.env.pos.db.get_product_by_id(scheme_prod_list[product].key);
                                            order.add_product(line_product, {
                                                discount: sch_qty_disc,
                                                quantity: qty_arranged_dict[dict_item].value
                                            });
                                            remained -= qty_arranged_dict[dict_item].value
                                        }
                                    }
                                }
                                if (remained > 0) {
                                    var line_product = this.env.pos.db.get_product_by_id(scheme_prod_list[product].key);
                                    order.add_product(line_product, {
                                        price: product_price,
                                        quantity: remained
                                    });

                                }
                                product_discounted = true
                                break;

                            }
                        } //END OF qty_arranged_dict
                        if (product_discounted == false) {
                            var line_product = this.env.pos.db.get_product_by_id(scheme_prod_list[product].key);
                            order.add_product(line_product, {
                                quantity: scheme_prod_list[product].value
                            });
                        }
                    } //END OF scheme_prod_list

                } //END Of unit_price_disc_percent

                ////////////////////////////////////////////////////////////////////////////
                //            Volume Discount
                ////////////////////////////////////////////////////////////////////////////
                else if (schemes[s].scheme_type == 'volume_discount') {
                    for (var n = 0; n < avail.length; n++) {
                        var orderline_data_new = [];
                        var volume_neworderLines = order.get_orderLineCollection_obj();
                        var volume_prod_list = this.get_available_on_product_list(avail[n]);

                        //First line's available products

                        var gqty = 0;
                        var lin = new Array();
                        var buy_id = new Array();
                        var volume_bqty = 0;
                        for (var p = 0; p < volume_prod_list.length; p++) {
                            //Check if product is available in orderline
                            for (var o = 0; o < orderlines.length; o++) {

                                if (volume_prod_list[p] == orderlines[o].get_product().id) {

                                    orderline_data_new.push({
                                        org_id: orderlines[o].get_product().id,
                                        org_quantity: orderlines[o].quantity,
                                        org_price: orderlines[o].price
                                    });

                                    volume_bqty += orderlines[o].quantity;
                                    volume_neworderLines.add(orderlines[o]);
                                    lin.push(orderlines[o].quantity)
                                    order.remove_orderline(orderlines[o]);
                                    buy_id.push(orderlines[o].get_product().id)
                                }
                            }
                        } //prod list

                        var temp_orderline_data_new = []
                        //merge repeated product qty
                        for (var x in orderline_data_new) {
                            if (temp_orderline_data_new.length == 0) {
                                temp_orderline_data_new.push({
                                    new_id: orderline_data_new[x].org_id,
                                    new_qty: orderline_data_new[x].org_quantity,
                                    new_price: orderline_data_new[x].org_price
                                });
                            } else {
                                var flag = false
                                for (y in temp_orderline_data_new) {


                                    if (temp_orderline_data_new[y].new_id == orderline_data_new[x].org_id) {
                                        temp_orderline_data_new[y].new_qty += orderline_data_new[x].org_quantity
                                        flag = true
                                    }
                                }
                                if (flag == false) {
                                    temp_orderline_data_new.push({
                                        new_id: orderline_data_new[x].org_id,
                                        new_qty: orderline_data_new[x].org_quantity,
                                        new_price: orderline_data_new[x].org_price
                                    });
                                }
                            }
                        }

                        temp_orderline_data_new.sort(function(a, b) {
                            return (b.new_price) - (a.new_price)
                        })

                        var volume_singleton_array = new Array()
                        j = 1;
                        for (var product in temp_orderline_data_new) {
                            for (var i = 0; i < temp_orderline_data_new[product].new_qty; i++) {
                                volume_singleton_array.push({
                                    volume_id: j,
                                    volume_product_id: temp_orderline_data_new[product].new_id,
                                    volume_price: temp_orderline_data_new[product].new_price,
                                    volume_qty: 1
                                });
                                j++

                            }
                        }


                        var sum_price = 0;
                        var qty_in_each_loop = 0;
                        var qty_counter = 0;
                        var price_counter = 0;
                        var singleton_counter = 0;
                        var qty_to_discount = 0;
                        var total_qty_to_discount = 0;
                        var remained_product_ids = new Array();

                        qty_to_discount = Math.floor(volume_bqty / schemes[s].buy_a_qty_in_volume)
                        total_qty_to_discount = qty_to_discount * schemes[s].buy_a_qty_in_volume


                        var stock_flag = false;
                        if (volume_bqty >= schemes[s].buy_a_qty_in_volume) {
                            qty_counter = 0;
                            price_counter = 0;

                            for (var prd = 0; prd < volume_singleton_array.length; prd++) {
                                var prod_ids_array = new Array();
                                qty_counter += volume_singleton_array[prd].volume_qty
                                price_counter += volume_singleton_array[prd].volume_price
                                remained_product_ids.push(volume_singleton_array[prd].volume_product_id)
                                if (qty_counter == schemes[s].buy_a_qty_in_volume) {
                                    for (var p = 0; p < schemes[s].buy_a_qty_in_volume; p++) {
                                        var sum_qty = 0;
                                        var total_price = 0;
                                        var price_difference = 0;
                                        var prod_percentage = 0;
                                        var total_percentage = 0;
                                        var final_price = 0;
                                        var disc = 0;

                                        price_difference = (price_counter - schemes[s].offer_price)
                                        prod_percentage = (volume_singleton_array[p].volume_price / price_counter);
                                        total_percentage = (prod_percentage * price_difference).toFixed(2)
                                        final_price = (volume_singleton_array[p].volume_price - total_percentage)
                                        //					    		disc = ((total_percentage/volume_singleton_array[p].volume_price)*100).toFixed(2)

                                        disc = schemes[s].offer_price / schemes[s].buy_a_qty_in_volume
                                        if (stock_flag == true) {
                                            var line_product = pos_obj.db.get_product_by_id(remained_product_ids[p]);
                                            order.add_product(line_product, {
                                                price: disc,
                                                merge: true,
                                                merge_flag: true,
                                                stock: true
                                            });
                                            stock_flag = false;
                                        } else {
                                            var line_product = pos_obj.db.get_product_by_id(remained_product_ids[p]);
                                            order.add_product(line_product, {
                                                price: disc,
                                                merge: true,
                                                merge_flag: true
                                            });
                                        }

                                    }
                                    qty_counter = 0;
                                    price_counter = 0;
                                    remained_product_ids = [];
                                    stock_flag = true
                                }
                            }
                            //REMAINED
                            if (remained_product_ids.length != 0) {
                                for (i = 0; i < remained_product_ids.length; i++) {

                                    var line_product = pos_obj.db.get_product_by_id(remained_product_ids[i]);
                                    order.add_product(line_product, {
                                        quantity: 1
                                    });
                                }
                            }
                            qty_counter = 0;
                            price_counter = 0;
                            remained_product_ids = []
                        } else //NOT ENOUGH QTY
                        {

                            volume_neworderLines.each(function(orderline) {
                                var line_product = pos_obj.db.get_product_by_id(orderline.get_product().id);
                                order.add_product(line_product, {
                                    price: orderline.price,
                                    quantity: orderline.quantity
                                });
                            });
                        }

                    } //avail loop
                } // end of volume discount

            } //end of scheme for loop
            if (modified_orderlines) {
                modified_orderlines.each(function(orderline) {
                    var line_product = pos_obj.db.get_product_by_id(orderline.get_product().id);
                    order.add_product(line_product, {
                        quantity: orderline.quantity,
                        discount: orderline.discount
                    });
                });
            }
            if (new_q.length != 0) {
                for (var i = 0; i < get_product_id_list.length; i++) {
                    var line_product = this.env.pos.db.get_product_by_id(get_product_id_list[i]);
                    order.add_product(line_product, {
                        quantity: new_q[0],
                        discount: scheme_discount
                    });
                }
            }

        }
        get_product_details(id) {
            var product_list = this.env.pos.product_obj;
            for (var k = 0; k < product_list.length; k++) {
                if (product_list[k].id == id) {
                    return product_list[k];
                }
            }
        }
        get_available_on_product_list(id) {
            var available_on = this.env.pos.available_on_list; //Getting records from loyalty.available_on
            for (var l = 0; l < available_on.length; l++) {
                if (available_on[l].id == id) {
                    return available_on[l].product_list;
                }
            }
        }
        get_scheme_qty(id) {
            var qty_on = this.env.pos.qty_disc; //Getting records from loyalty.available_on
            for (var l = 0; l < qty_on.length; l++) {
                if (qty_on[l].id == id) {
                    return qty_on[l].qty;
                }
            }

        }
        get_scheme_discount(id) {
            var qty_on = this.env.pos.qty_disc; //Getting records from loyalty.available_on
            for (var l = 0; l < qty_on.length; l++) {
                if (qty_on[l].id == id) {
                    return qty_on[l].discount;
                }
            }
        }
        get_product_price(id) {
            var product_obj = this.env.pos.prod_temp; //Getting records from loyalty.available_on
            for (var l = 0; l < product_obj.length; l++) {
                if (product_obj[l].id == id) {
                    return product_obj[l].list_price;
                }
            }
        }
        get_available_on_template_list(id) {
            var available_on = this.env.pos.available_on_list; //Getting records from loyalty.available_on
            for (var l = 0; l < available_on.length; l++) {
                if (available_on[l].id == id) {
                    return available_on[l].template_id[0];
                }
            }
        }
        buy_product_exists(buy_id_array, orderline_prod_id) {
            for (var l = 0; l < buy_id_array.length; l++) {
                if (buy_id_array[l] == orderline_prod_id) {
                    return true;
                }
            }
        }


        async onClick() {
            await this.apply_scheme();
        }
    }

    CheckSchemeWidget.template = 'CheckSchemeWidget';
    ProductScreen.addControlButton({
        component: CheckSchemeWidget,
        condition: function() {
            return this;
        },
    });
    Registries.Component.add(CheckSchemeWidget);
    return CheckSchemeWidget;
});