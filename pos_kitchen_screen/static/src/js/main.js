/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_kitchen_screen.main', function (require) {
	"use strict";
	var models = require('point_of_sale.models');
	var SuperOrder = models.Order.prototype;
	var rpc = require('web.rpc');



	models.load_models([{
		model: 'pos.kitchen.screen.config',
		label: 'Pos Kitchen Screen',
		fields: ['pos_config_ids', 'queue_order', 'pos_category_ids', 'url', 'ip_address'],
		loaded: function (self, result) {
			self.db.pos_screen_data = {};
			self.db.recent_notifications = [];
			_.each(result, function (data) {
				if (data && (data.pos_config_ids.indexOf(self.config.id) != -1)) {
					self.db.pos_screen_data[data.id] = data;
				}
			});
		}
	}], {
		'after': 'pos.config'
	});

	models.Order = models.Order.extend({


		get_queue_no: function () {
			var self = this;
			return self.pos.get_order().token_number;
		},


		export_as_JSON: function () {
			var self = this;
			var loaded = SuperOrder.export_as_JSON.call(this);
			loaded.is_kitchen_order = self.validate_order_for_kitchen();
			loaded.token_no = self.token_no;
			return loaded;
		},
		add_paymentline: function(cashregister) {
			SuperOrder.add_paymentline.call(this,cashregister);
			var self = this;
			console.log("chekcs to add",self.pos.get_order().token_no ,self.pos.get_order().validate_order_for_kitchen())
			if (!self.pos.config.order_action || (self.pos.config.order_action && self.pos.config.order_action == 'validation')){
				if(!self.pos.get_order().token_no && self.pos.get_order().validate_order_for_kitchen())
					self.add_token_number();
			}
		},
		add_token_number:function(){
			var self = this;
			var res = rpc.query({
				method:'get_token_number',
				model:'pos.order',
			}).then(function(res){
				console.log("tokneennnnn*****",res)
				self.pos.get_order().token_no = res;
			}).catch(function(e){
				console.log("e",e)
			})
			return res;
		},
		validate_order_for_kitchen: function () {
			var self = this;
			var screen_data = self.pos.db.pos_screen_data;
			var is_kitchen_order = false;
			var pos_categ_ids = []
			_.each(self.pos.db.pos_screen_data, function (data) {
				pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
			});
			if (screen_data && !self.is_return_order) {
				if (screen_data && !pos_categ_ids)
					is_kitchen_order = true;
				if (!is_kitchen_order)
					_.each(self.get_orderlines(), function (line) {
						if (line.product.pos_categ_id) {
							_.each(line.product.pos_categ_id, function (cat) {
								if (pos_categ_ids && pos_categ_ids.indexOf(cat) != -1)
									is_kitchen_order = true
							})
						}

					})
			}

			return is_kitchen_order
		}

	});

});
