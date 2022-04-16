odoo.define('point_of_sale.ReloadStockOnHand', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const {posbus} = require('point_of_sale.utils');

    class ReloadStockOnHand extends PosComponent {
        constructor() {
            super(...arguments);
        }

        async onClick() {
            await this._reloadStockOnHand()
            this.showPopup('ConfirmPopup', {
                title: this.env._t('Reload Stock Successfully !'),
                body: this.env._t('All Products just updated stock on hand the same with backend.'),
            })
            posbus.trigger('pos.sync.stock')
        }

        async _reloadStockOnHand() {
            await this.env.pos.getStockDatasByLocationIds([], this.env.pos.stock_location_ids)
        }
    }

    ReloadStockOnHand.template = 'ReloadStockOnHand';

    Registries.Component.add(ReloadStockOnHand);

    return ReloadStockOnHand;
});
