odoo.define('pos_retail.ClosePosPopup', function (require) {
    'use strict';

    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');

    const RetailClosePosPopup = (ClosePosPopup) =>
        class extends ClosePosPopup {
            // async closeSession() {
            //     let {confirmed, payload: result} = await this.showPopup('ConfirmPopup', {
            //         title: this.env._t('Are you sure closing current Session'),
            //         body: this.env._t('If yes, please click to Confirm button.'),
            //         cancelButtonText: this.env._t('Keep Selling'),
            //         confirmButtonText: this.env._t('Confirm'),
            //     })
            //     if (confirmed) {
            //         return await super.closeSession()
            //     }
            // }
        };

    Registries.Component.extend(ClosePosPopup, RetailClosePosPopup);
    return RetailClosePosPopup

});
