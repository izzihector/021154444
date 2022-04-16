odoo.define('pos_product_addons.product_addons', function (require) {
    "use strict";

      const { useListener } = require('web.custom_hooks');
      const NumberBuffer = require('point_of_sale.NumberBuffer');
      const PosComponent = require('point_of_sale.PosComponent');
      const Registries = require('point_of_sale.Registries');
      const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
      const { useState } = owl.hooks;

      const ProductScreen = require('point_of_sale.ProductScreen');
        const PosProductAddons = ProductScreen =>
        class extends ProductScreen {


           async _clickProduct(event) {
            if (!this.currentOrder) {
                this.env.pos.add_new_order();
            }
            const product = event.detail;
            const options = await this._getAddProductOptions(product);
            if (product){
                this.env.pos.get_addon_list(product.id);
            }
            // Do not add product if options is undefined.
            if (!options) return;
            // Add the product after having the extra information.
            this.currentOrder.add_product(product, options);
            NumberBuffer.reset();

        }



         _add_to_orderline (event) {
            if (event.target.className == 'addons-product' || event.target.className == 'addons-item'){
                    var order = this.env.pos.get('selectedOrder');
                    if (event.target.className == 'addons-product'){
                        var addon_id = event.target.offsetParent.dataset.addonId;
                    }else{
                        var addon_id = event.target.dataset.addonId;
                    }
                    var addon_obj = this.env.pos.db.get_product_by_id([addon_id]);
                    if (addon_obj.taxes_id.length > 0){
                        var addon_obj_tax = this.env.pos.taxes_by_id[addon_obj.taxes_id[0]].amount;
                    }else{
                        var addon_obj_tax = 0;
                    }

                    //added code to add as order line
//                    order.add_product(addon_obj)    //code modified

                    var selected_line = order.selected_orderline;
                    if (!selected_line) {
                        alert('You have to select the corresponding product fist');

                    } else {
                        var total_price = 0.00;
                        for (var i = 0; i < selected_line.product.addon_ids.length; i++) {
                            if (addon_obj.id == selected_line.product.addon_ids[i]) {
                                total_price += parseFloat(addon_obj.lst_price) + parseFloat(parseFloat(((parseFloat(addon_obj.lst_price)*parseFloat(addon_obj_tax))/100)).toFixed(2)); // Change the value of the price


                            }
                        }
                        order.selected_orderline.price += total_price;
                        order.selected_orderline.trigger('change', order.selected_orderline);

                        var addons = order.selected_orderline.addon_items;
                        var has_already = false;

                        var add_prod_id = []
                        for (var i = 0; i < addons.length; i++) {
                            add_prod_id.push(addons[i]['addon_id'])
                            if (addons[i]['addon_id'] == addon_obj.id) {
                                has_already = true;
                                addons[i]['addon_count'] += 1
                                addons[i]['total_without'] += addon_obj.lst_price
                                addons[i]['total_with'] += parseFloat(addon_obj.lst_price) + parseFloat(parseFloat(((parseFloat(addon_obj.lst_price)*parseFloat(addon_obj_tax))/100)).toFixed(2))


                            }


                        }

                 if (add_prod_id.includes(addon_obj.id) == false){
                        addons.push(
                            {
                                'addon_id': addon_obj.id,
                                'addon_name': addon_obj.display_name,
                                'addon_price_without': addon_obj.lst_price,
                                'addon_price_with': parseFloat(addon_obj.lst_price) + parseFloat(parseFloat(((parseFloat(addon_obj.lst_price)*parseFloat(addon_obj_tax))/100)).toFixed(2)),
                                'addon_uom': addon_obj.uom_id[1],
                                'addon_count': addon_obj.uom_id[0],
                                'total_without': addon_obj.lst_price * addon_obj.uom_id[0],
                                'total_with': (parseFloat(addon_obj.lst_price) + parseFloat(parseFloat(((parseFloat(addon_obj.lst_price)*parseFloat(addon_obj_tax))/100)).toFixed(2))) * addon_obj.uom_id[0],
                                'tax': addon_obj.taxes_id[0],
                            }
                        );
                        }

                        order.selected_orderline.trigger('change', order.selected_orderline);
                    }

            }
        }


        };
    Registries.Component.extend(ProductScreen, PosProductAddons);
    return ProductScreen;


});
