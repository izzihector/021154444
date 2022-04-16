odoo.define('pos_customer_load_warehouse.LoadCustomerWarehouseWise', function (require) {
    'use strict';

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');

    const PosLoadCustomerWarehouse = (ClientListScreen) =>
        class extends ClientListScreen {
            /**
             * @override
             */
            async getNewClient() {
            	const  warehouse_id = this.env.pos.config.warehouse_id;
				var domain = [];
				if(this.state.query) {
					domain = [
						["name", "ilike", this.state.query + "%"],
						["warehouse_id", "=", warehouse_id[0]]
					];
				}else{
					domain = [
						["warehouse_id", "=", warehouse_id[0]]
					];
				}
				console.log("domain:", domain);
				var fields = _.find(this.env.pos.models, function(model){ return model.label === 'load_partners'; }).fields;
				var result = await this.rpc({
					model: 'res.partner',
					method: 'search_read',
					args: [domain, fields],
					kwargs: {
						limit: 10,
					},
				},{
					timeout: 3000,
					shadow: true,
				});

				return result;
			}
        };

    Registries.Component.extend(ClientListScreen, PosLoadCustomerWarehouse);

    return ClientListScreen;
});
