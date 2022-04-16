odoo.define('pos_product_addons.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');



    models.load_fields('product.product', ['addon_ids', 'has_addons']);

    var _super_pos = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        get_addon_list: function (product_id) {
            // Calls once clicks on the product and shows its add-ons.
            var self = this;
            $('.addon-contents').empty();
            var product = self.db.get_product_by_id(product_id);
            var element = [];
            if (product.addon_ids.length) {
                var $addonpane = $('.addonpane');
                if (this.env.isMobile){
                    $('.product-list-container').css("width", "70%");
                    $addonpane.css("visibility", "visible");
                    $addonpane.css("width", "30%");

                }else{
                    $('.product-list-container').css("width", "80%");
                    $addonpane.css("visibility", "visible");
                    $addonpane.css("width", "13.1%");
                }
                var display_name = '('+product.display_name+')'
                $('.sub-head').text(display_name).show('fast');
                for (var item = 0; item < product.addon_ids.length; item++) {
                    var product_obj = self.db.get_product_by_id([product.addon_ids[item]]);
                    if (product_obj) {
                        element = product_obj.display_name;
                        $('.addons-table').append(
                            '<tr class="addon-contents" class="row" style="width: 100%;">' +
                            '<td class="addons-item" style="width: 100%;" data-addon-id=' + product_obj.id + '> ' +
                            '<div class="addons-product" style="display: inline-block; width: 80%;">' + element + '</div>' +
                            '</div></td>' +
                            '</tr>');
                    }
                }
            } else {
                self.hide_addons()
            }

        },
        hide_addons: function () {
            var $layout_table = $('.product-list-container');
            $layout_table.removeAttr("width");
            $layout_table.css("width", "100%");
            $('.addonpane').css("visibility", "hidden");
        },



    });


    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            _super_orderline.initialize.call(this, attr, options);
            this.addon_items = this.addon_items || [];
        },

        init_from_JSON: function (json) {
            _super_orderline.init_from_JSON.apply(this, arguments);
            this.addon_items = json.addon_items || [];

        },
        export_as_JSON: function () {
            var json = _super_orderline.export_as_JSON.apply(this, arguments);
            json.addon_items = this.addon_items || [];
            return json;
        },
        can_be_merged_with: function (orderline) {
            if (orderline.product.has_addon) {
                return false;
            } else {
                return _super_orderline.can_be_merged_with.apply(this, arguments);
            }
        },
        //used to create a json of the ticket, to be sent to the printer

        export_for_printing: function(){

        return {
            id: this.id,
            quantity:           this.get_quantity(),
            unit_name:          this.get_unit().name,
            price:              this.get_unit_display_price(),
            discount:           this.get_discount(),
            product_name:       this.get_product().display_name,
            product_name_wrapped: this.generate_wrapped_product_name(),
            price_lst:          this.get_lst_price(),
            display_discount_policy:    this.display_discount_policy(),
            price_display_one:  this.get_display_price_one(),
            price_display :     this.get_display_price(),
            price_with_tax :    this.get_price_with_tax(),
            price_without_tax:  this.get_price_without_tax(),
            price_with_tax_before_discount:  this.get_price_with_tax_before_discount(),
            tax:                this.get_tax(),
            product_description:      this.get_product().description,
            product_description_sale: this.get_product().description_sale,
            orderline_id :          this.id,
        };
    },

        get_addon_uom: function (id) {
            for (var i = 0; i <= this.addon_items.length; i++) {
                if (this.addon_items[i]['addon_id'] == id) {
                    return this.addon_items[i]['addon_uom']
                }
            }

        }
    });

    });