odoo.define('pos_product_addons.orderline', function (require) {
    "use strict";

    const Registries = require('point_of_sale.Registries');

    const Orderline = require('point_of_sale.Orderline');
    const PosOrderLineAddons = Orderline =>
    class extends Orderline {


        selectLine() {
            this.trigger('select-line', { orderline: this.props.line });
            this.env.pos.get_addon_list(this.props.line.product.id);
        }

        };


    Registries.Component.extend(Orderline, PosOrderLineAddons);
    return Orderline;


});