odoo.define('stock_movement_report.inventory_movement_report', function (require) {
'use strict';

const core = require('web.core');
const framework = require('web.framework');
const session = require('web.session');
const AbstractAction = require('web.AbstractAction');
const datepicker = require('web.datepicker');
const RelationalFields = require('web.relational_fields');
const StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
const Widget = require('web.Widget');
const Pager = require('web.Pager');
const field_utils = require('web.field_utils');
const QWeb = core.qweb;
const _t = core._t;

const { ComponentWrapper } = require('web.OwlCompatibility');

var M2MFilters = Widget.extend(StandaloneFieldManagerMixin, {

    init: function (parent, fields) {
        this._super.apply(this, arguments);
        StandaloneFieldManagerMixin.init.call(this);
        this.fields = fields;
        this.widgets = {};
    },

    willStart: function () {
        var self = this;
        var defs = [this._super.apply(this, arguments)];
        _.each(this.fields, function (field, fieldName) {
            defs.push(self._makeM2MWidget(field, fieldName));
        });
        return Promise.all(defs);
    },

    start: function () {
        var self = this;
        var defs = [this._super.apply(this, arguments)];
        _.each(this.fields, function (field, fieldName) {
            self.$el.append($('<p/>', {style: 'font-weight:bold;'}).text(field.label));
            defs.push(self.widgets[fieldName].appendTo(self.$el));
        });
        return Promise.all(defs);
    },

    _confirmChange: function () {
        var self = this;
        var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
        var data = {};
        _.each(this.fields, function (filter, fieldName) {
            data[fieldName] = self.widgets[fieldName].value.res_ids;
        });
        this.trigger_up('m2m_value_changed', data);
        return result;
    },

    _makeM2MWidget: function (fieldInfo, fieldName) {
        var self = this;
        var options = {};
        options[fieldName] = {
            options: {
                no_create_edit: true,
                no_create: true,
            },
        };
        return this.model.makeRecord(fieldInfo.modelName, [{
            fields: [{
                name: 'id',
                type: 'integer',
            }, {
                name: 'display_name',
                type: 'char',
            }],
            name: fieldName,
            relation: fieldInfo.modelName,
            type: 'many2many',
            value: fieldInfo.value,
            domain: fieldInfo.domain
        }], options).then(recordID => {
            self.widgets[fieldName] = new RelationalFields.FieldMany2ManyTags(self,
                fieldName,
                self.model.get(recordID),
                {mode: 'edit',}
            );
            self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
        });
    },
});

var InventoryMovementReportAction = AbstractAction.extend({ //ControlPanelMixin, 
    hasControlPanel: true,

    custom_events: {
        'm2m_value_changed': function(ev) {
            var self = this;
            var key = _.keys(ev.data)[0];
            self.search_filters[key] = ev.data[key];
            return self.reload().then(() => {
                self.$searchview_buttons.find('.stock_' + key + '_filter').click();
            });
        },
    },

    events: {
        'click .o_product_link': 'open_product',
    },

    init: function(parent, action) {
        this._super.apply(this, arguments);
        this.actionManager = parent;
        this.report_model = action.context.model;
        if (this.report_model === undefined) {
            this.report_model = 'inventory.movement.report';
        };
        if (action.context.id) {
            this.inv_movement_report_id = action.context.id;
        };
        this.odoo_context = action.context;
        this.search_options = {};
        this.pagerState = { //default pager options
                limit: 80,
                offset: 0,
            };
        this.search_filters = this._buildSearchFilters();
        if (sessionStorage.getItem('inventory_movement_report_options')) {
            this.search_filters = JSON.parse(sessionStorage.getItem('inventory_movement_report_options')) || this.search_filters;
        };
        this.M2MFilters = {};
    },
    start: async function() {
        await this._super(...arguments);
        this.get_html().then(this.render.bind(this));
    },
    open_product: function(e){
        this.do_action({
            type: 'ir.actions.act_window',
            res_model: "product.product",
            res_id: parseInt($(e.target).data('product')),
            views: [[false, 'form']],
        });
    },
    get_html: function() {
        var self = this;
        return this._rpc({
            model: 'inventory.movement.report',
            method: 'get_html',
            args: [self.search_filters, self.pagerState],
            kwargs: {context: session.user_context},
        }).then(result => {
            return self.parseReportsInformations(result);
        });
    },
    parseReportsInformations: function(values) {
        this.html = values.html;
        this.buttons = values.buttons;
        this.search_options = values.search_options;
        this.search_filters = values.search_filters;
        this.records_count = values.records_count;
        this.pagerState = values.pagerState;
        // this.pagerState.limit = values.limit_per_page;
        this.persist_options();
    },
    persist_options: function() {
        sessionStorage.setItem('inventory_movement_report_options', JSON.stringify(this.search_filters));
    },
    render: async function() {
        var self = this;
        // self.$el.html(self.html);
        self.$el.find('.o_content').html(self.html);
        await self.update_cp();
    },
    reload: function() {
        var self = this;
        return self.get_html().then(() => {
            self.render();
        });
    },
    _shouldRenderPager: function (currentMinimum, limit, size) {
        if (!limit || !size) {
            return false;
        }
        const maximum = Math.min(currentMinimum + limit - 1, size);
        const singlePage = (1 === currentMinimum) && (maximum === size);
        return !singlePage;
    },
    _renderGroupPager: function () {
        var self = this;
        const currentMinimum = this.pagerState.offset + 1;
        const limit = this.pagerState.limit;
        const size = this.records_count;
        // check limit and only render pager if needed
        if (!this._shouldRenderPager(currentMinimum, limit, size)) {
            return;
        };

        // check and destroy old pager
        if (this.pager) {
            this.pager.destroy();
            this.pager = null;
        };

        this.pager = new ComponentWrapper(this, Pager, { currentMinimum, limit, size });
        const pagerMounting = this.pager.mount(this.$('.o_cp_pager').get(0)).then(() => {
            // Event binding is done here to get the related group and wrapper.
            self.pager.el.addEventListener('pager-changed', ev => {
                ev.stopPropagation();
                const { currentMinimum, limit } = ev.detail;
                self.pagerState = {
                        limit: limit,
                        offset: currentMinimum - 1,
                    }
                self.reload();
            });
            self.pager.el.addEventListener('click', ev => ev.stopPropagation());
        });
    },
    update_cp: function() {
        if (!this.$buttons) {
            this.renderButtons();
        }
        this.render_searchview_buttons();
        this._renderGroupPager();
        this.controlPanelProps.cp_content = {
            $buttons: this.$buttons,
            $searchview_buttons: this.$searchview_buttons
        }
        this.updateControlPanel();
    },
    do_show: function() {
        this._super();
        this.update_cp();
    },
    renderButtons: function() {
        var self = this;
        this.$buttons = $(QWeb.render("inventoryReports.buttons", {buttons: this.buttons}));
        // bind actions
        _.each(this.$buttons.siblings('button'), function(el) {
            $(el).click(function() {
                self.search_filters.pagerState = self.pagerState;
                return self._rpc({
                    model: self.report_model,
                    method: $(el).attr('action'),
                    args: [self.inv_movement_report_id, self.search_filters],
                    context: self.odoo_context,
                })
                .then(result => {
                    var def = $.Deferred();
                    session.get_file({
                        url: '/action_report_print',
                        data: {data: JSON.stringify(result.data)},
                        success: def.resolve.bind(def),
                        error: (error) => self.call('crash_manager', 'rpc_error', error),
                        complete: framework.unblockUI,
                    });
                    return def;
                });
            });
        });
        return this.$buttons;
    },
    render_searchview_buttons: function() {
        var self = this;
        this.$searchview_buttons = $(QWeb.render("inventoryReports.searchOptions", {options: self.search_options, filters: self.search_filters}));
        // bind searchview buttons/filter to the correct actions
        var $datetimepickers = this.$searchview_buttons.find('.js_stock_reports_datetimepicker');
        var options = { // Set the options for the datetimepickers
            locale : moment.locale(),
            format : 'L',
            icons: {
                date: "fa fa-calendar",
            },
        };
        // attach datepicker
        $datetimepickers.each(function () {
            var name = $(this).find('input').attr('name');
            var defaultValue = $(this).data('default-value');
            $(this).datetimepicker(options);
            var dt = new datepicker.DateWidget(options);
            dt.replace($(this)).then(() => {
                dt.$el.find('input').attr('name', name);
                if (defaultValue) { // Set its default value if there is one
                    dt.setValue(moment(defaultValue));
                };
            });
        });
        // format date that needs to be show in user lang
        _.each(this.$searchview_buttons.find('.js_format_date'), function(dt) {
            var date_value = $(dt).html();
            $(dt).html((new movement(date_value)).format('ll'));
        });
        // fold all menu
        this.$searchview_buttons.find('.js_foldable_trigger').click(function (event) {
            $(this).toggleClass('o_closed_menu o_open_menu');
            self.$searchview_buttons.find('.o_foldable_menu[data-filter="'+$(this).data('filter')+'"]').toggleClass('o_closed_menu o_open_menu');
        });
        this.$searchview_buttons.find('.js_stock_report_date_filter').click(function (event) {
            self.search_filters.date.filter = $(this).data('filter');
            var error = false;
            if ($(this).data('filter') === 'custom') {
                var date_from = self.$searchview_buttons.find('.o_datepicker_input[name="date_from"]');
                var date_to = self.$searchview_buttons.find('.o_datepicker_input[name="date_to"]');
                if (date_from.length > 0){
                    error = date_from.val() === "" || date_to.val() === "";
                    self.search_filters.date.date_from = field_utils.parse.date(date_from.val());
                    self.search_filters.date.date_to = field_utils.parse.date(date_to.val());
                } else {
                    error = date_to.val() === "";
                };
            };
            if (error) {
                self.call('crash_manager', 'show_warning', {
                    message: _t('Date cannot be empty'),
                }, {
                    sticky: false,
                });
            } else {
                self.reload();
            };
        });
        _.each(this.search_options.m2m_filters, function(option) {
            var fields = {};
            fields[option.field] = {
                label: option.label,
                modelName: option.model,
                value: self.search_filters[option.field].map(Number),
                domain: option.domain
            };
            if (!_.isEmpty(fields)) {
                self.M2MFilters[option.field] = new M2MFilters(self, fields);
                self.M2MFilters[option.field].appendTo(self.$searchview_buttons.find('.js_stock_' + option.field + '_m2m'));
            };
        });

        _.each(this.$searchview_buttons.find('.js_switch_choice_filter'), function(k) {
            $(k).toggleClass('selected', ''+self.search_filters[$(k).data('field')] === ''+$(k).data('id'));
        });

        this.$searchview_buttons.find('.js_switch_choice_filter').click(function (event) {
            self.search_filters[$(this).data('field')] = $(this).data('id');
            self.reload();
        });

    },

    _buildSearchFilters: function () {
        return {
            'date': {'filter': 'today', 'date_from': '', 'date_to': ''},
            'company_id': NaN,
            'products': [],
            'categories': [],
            'warehouses': [],
            'locations': []
        }
    },
});

core.action_registry.add("inventory_movement_report", InventoryMovementReportAction);
return InventoryMovementReportAction;
});
