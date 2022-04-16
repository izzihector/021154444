odoo.define('pos_promotional_scheme.models', function (require) {
"use strict";

	var models = require('point_of_sale.models');

    models.load_models([{
        model:  'loyalty.promotional.schemes',
        fields: ['id','name','from_date','to_date','scheme_type','scheme_basis','available_on','scheme_product',
      		    'buy_a_qty','get_a_qty','discount','qty_disc','buy_a_qty_in_volume','offer_price'],
        loaded: function(self, scheme) {
            self.scheme = scheme;
        }
    },
    ]);


    models.load_models([{
        model:  'loyalty.available_on',
        fields: ['id','template_id','product_list'],
        domain: function(self){ return []; },
        loaded: function(self, available_on_list) {
            self.available_on_list = available_on_list;
        }
    },
    ]);



    models.load_models([{
        model:  'loyalty.qty.disc',
        fields: ['id','qty','discount'],
        domain: function(self){ return []; },
        loaded: function(self, qty_disc) {
            self.qty_disc = qty_disc;
        }
    },
    ]);


var OrderlineCollection = Backbone.Collection.extend({
	    model: models.Orderline,
	});

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
get_orderLineCollection_obj : function(){
			return new OrderlineCollection();
		},
});






});

