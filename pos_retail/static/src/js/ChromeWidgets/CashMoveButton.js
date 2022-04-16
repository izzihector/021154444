odoo.define('pos_retail.CashMoveButton', function (require) {
    'use strict';

    const CashMoveButton = require('point_of_sale.CashMoveButton');
    const Registries = require('point_of_sale.Registries');

    const RetailCashMoveButton = (CashMoveButton) =>
        class extends CashMoveButton {
            constructor() {
                super(...arguments);
            }

            onClick() {
                if (!this.env.pos.config.cash_control) {
                    return this.showPopup('ErrorPopup', {
                        title: this.env._t('Cash control not active with your point of sale'),
                        body: this.env._t('You need minimum 1 POS Payment Method with journal with type is Cash, and add it to your pos.')
                    })
                }
                super.onClick()
            }
        }
    Registries.Component.extend(CashMoveButton, RetailCashMoveButton);

    return RetailCashMoveButton;
});
