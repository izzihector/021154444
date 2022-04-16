odoo.define('pos_loyalty_management.WkLoyaltyAlertPopUp', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class WkLoyaltyAlertPopUp extends AbstractAwaitablePopup {
    }
    WkLoyaltyAlertPopUp.template = 'WkLoyaltyAlertPopUp';
    WkLoyaltyAlertPopUp.defaultProps = {
        title: 'Confirm ?',
        body: '',
    };

    Registries.Component.add(WkLoyaltyAlertPopUp);

    return WkLoyaltyAlertPopUp;


});