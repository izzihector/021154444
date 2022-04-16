odoo.define('pos_sequence_refund.TicketScreen', function (require) {
    'use strict';

    const models = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
	const TicketScreen = require('point_of_sale.TicketScreen');    
	
	const myTicketScreen = (TicketScreen) =>
		class extends TicketScreen {
			/**
         * Fetches the done orders from the backend that needs to be shown.
         * If the order is already in cache, the full information about that
         * order is not fetched anymore, instead, we use info from cache.
         */
        async _fetchSyncedOrders() {
            const domain = this._computeSyncedOrdersDomain();
            const limit = this._state.syncedOrders.nPerPage;
            const offset = (this._state.syncedOrders.currentPage - 1) * this._state.syncedOrders.nPerPage;
            const { ids, totalCount } = await this.rpc({
                model: 'pos.order',
                method: 'search_paid_order_ids',
                kwargs: { config_id: this.env.pos.config.id, domain, limit, offset },
                context: this.env.session.user_context,
            });
            const idsNotInCache = ids.filter((id) => !(id in this._state.syncedOrders.cache));
			var sequence_number = this.env.pos.pos_session.sequence_number;
            if (idsNotInCache.length > 0) {
                const fetchedOrders = await this.rpc({
                    model: 'pos.order',
                    method: 'export_for_ui',
                    args: [idsNotInCache],
                    context: this.env.session.user_context,
                });
                // Cache these fetched orders so that next time, no need to fetch
                // them again, unless invalidated. See `_onInvoiceOrder`.
                fetchedOrders.forEach((order) => {
                    this._state.syncedOrders.cache[order.id] = new models.Order({}, { pos: this.env.pos, json: order });
                });
            }
			this.env.pos.pos_session.sequence_number = sequence_number;
            this._state.syncedOrders.totalCount = totalCount;
            this._state.syncedOrders.toShow = ids.map((id) => this._state.syncedOrders.cache[id]);
        }
		};
	Registries.Component.extend(TicketScreen, myTicketScreen);
	return TicketScreen;
});