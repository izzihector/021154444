odoo.define('action_manager_stock_reports.ActionManager', function (require) {
"use strict";

const ActionManager = require('web.ActionManager');
const framework = require('web.framework');
const session = require('web.session');

ActionManager.include({
    /**
     * Overrides to handle the 'ir_actions_stock_report_download' actions.
     *
     * @override
     * @private
     */
    _handleAction: function (action, options) {
        var self = this;
        if (action.type === 'ir_actions_stock_report_download') {
            framework.blockUI();
            var def = $.Deferred();

            session.get_file({
                url: '/action_report_print',
                data: action.data,
                success: def.resolve.bind(def),
                error: (error) => self.call('crash_manager', 'rpc_error', error),
                complete: framework.unblockUI,
            });
            return def;
        };
        return this._super.apply(this, arguments);
    },
});

});
