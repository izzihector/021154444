odoo.define('website_direct_order.direct_order', function (require) {
"use strict";
	var core = require('web.core');
	var _t = core._t;
	var ajax = require('web.ajax');
	var session = require('web.session');

	ajax.jsonRpc('/check/user/group', 'call',{}).then(function(val){
		if (!val.group){
			if($('a[href="/direct/order"]')){
				$('a[href="/direct/order"]').parent().remove();
			}
		}
		$('.do_th_unit_price').text('Unit Price (' + val.price_symbol + ')'  )
		$('.do_th_subtotal').text(' Subtotal (' + val.price_symbol + ')' )
    })

	var bs_model = '<div id="myModal" class="modal so_template_model show fade" style="display: block;" role="dialog">'+
  	'<div class="modal-dialog">' + 
	    '<div style = "background-color:aliceblue;" class="modal-content">' + 
	      '<div class="modal-header">' + 
	        '<h3 class="modal-title do_modal_title" style="color:green;">Warning!</h3>' + 
	      '</div>' + 
	      '<div class="modal-body" style="text-align:center;">' + 
	        '<b><h4 class="do_modal_body"></h4></b>' + 
	      '</div>' + 
	    '</div>' + 
	  '</div>' + 
	'</div>'

	$( document ).ready(function() {
		// --------------------------UPDATE SUBTOTAL WITH QTY ONCHANGE

		$('#do_qty').on('propertychange input', function (e) {
			var qty_val = this.value
			// var tr = $(this).parent().parent()
			var tr = $(this).closest('.do_tr');
			var unit_price = $(tr).find('#do_unit_price').val()
			var subtotal = qty_val *  unit_price 
    		$(tr).find('#do_subtotal').val(subtotal)
		});

		// --------------------------ADD ITEM ------------------

		$('.do_add_clone_tr').click(function() {
			$(".temp_lable_product").hide()
		  	var $clone =  $('#table').find('tr.table-line').clone(true).removeClass('d-none table-line').addClass('do_tr');
		  	$('#table').find('table').append($clone);
		  	$clone.find('#selProduct_Template').remove()
		  	// --------------------------SEARCH SELECT AND SELECT OPTION ADD
			$clone.find("#selProduct").select2({
				placeholder: " ---Select---",
				multiple: false,
				// minimumInputLength: 1,
				ajax: {
					url: "/do/search/product",
					dataType: 'json',
					quietMillis: 250,
				  	data: function(term, page) {
				      	return {
				        	name: term,
				        };
	    			},
				    results: function(data, page) {
				     	return {results: data};
     		 	    },
				    cache: true
				},
				formatResult: function(element){
				   	return element.text;
				},
				formatSelection: function(element){
				   	return element.text;
				},
				escapeMarkup: function(m) {
				   	return m;
				}
			});
			$('#s_template_name').removeClass('d-none')
			$('#do_create_so_template').removeClass('d-none')
			$('#set_template_name').removeClass('d-none')
			Select($clone)
		});

		function Select(clone) {
		    setTimeout(function(){
				clone.find('#selProduct').on('change',function(){
					var select_val = $(this).val()
					if(select_val != 0){
						var tr = $(this).closest('.do_tr');

				    	ajax.jsonRpc('/product/onchange/data', 'call',{'id':select_val}).then(function(val){
				    		if(val){
								var unit_price = $(tr).find('#do_qty').val()
					    		$(tr).find('#do_unit_price').val(val.price)
					    		$(tr).find('#do_subtotal').val(val.price * unit_price)
				    		}
				    	})
					}
				});
		   	},1000);
		};
		
		// ------------------------------ ADD NOTE ----------------------

		$('.do_add_note_tr').click(function(){
		  	var $clone =  $('#table').find('tr.do_note_tr').clone(true).removeClass('d-none do_note_tr').addClass('do_tr');
		  	$('#table').find('table').append($clone);
  		})

		//---------------------------- CREATE SALE ORDER --------------------------------

		$('.do_create').click(function() {
	 		var $do_tr = $('.do_tr')
			var data_list = []
			var create_qty = false
			var create_so = true
            $do_tr.each(function (x, y) {
				if ($(y).find('#selProduct').length == 1){
					var product =  $(y).find('#selProduct')
				}else{
					var product =  $(y).find('#selProduct_Template')
				}

				var product_value =  product.val()
				var quantity =  $(y).find('#do_qty')
				var quantity_value =  quantity.val()
				
				var comment =  $(y).find('textarea.my_do_comment')
				var comment_value =  comment.val()

				create_qty = quantity
				if(product.length != 0 && comment.length == 0){
					if(product_value > 0 && quantity_value == 0){
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product Quantity!')
			   		    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
			   		    return false;
					}

					if(product_value == 0 && quantity_value == 0){
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product and Quantity!')
			   		    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
			   		    return false;
					}

					if(product_value == 0 && quantity_value != 0){
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product!')
					    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
					    return false;
					}
					if(product_value > 0 && quantity_value != 0){
						var unit_price =  $(y).find('#do_unit_price').val()
						var data_dict  = {'product_id': parseInt(product_value) ,'product_uom_qty': parseInt(quantity_value)}
						data_list.push(data_dict)
					}
				}
				if(product.length == 0 && comment.length != 0){
					if(comment_value){
						var comment = {'comment':comment_value}
						data_list.push(comment)
					}else{
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Note!')
					   setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
						return false;
					}
				}

        	})

            if(data_list && create_so){
		    	ajax.jsonRpc('/do/create', 'call',{data_list}).then(function(val){
		    		if(val){
		    			window.location.href =  val
		    		}
		    	})	
            }
		});

		//--------------------------------- ADD SO template on Table----------------------------

		$('#so_template_select').on('propertychange input', function (e) {
			$('.temp_lable_product').show()
			var so_template = $(this).val()
	    	ajax.jsonRpc('/so/template', 'call',{so_template}).then(function(val){
	    		$('.do_tr').remove()

	    		if(val.length > 0){
	    			$('.temp_lable_product').hide()
		            $(val).each(function (x, y) {
		            	if(!y.comment){
	        			  	var $clone =  $('#table').find('tr.table-line').clone(true).removeClass('d-none table-line').addClass('do_tr do_tr_template');
						  	$clone.find('#do_qty').val(y.product_uom_qty)
						  	$clone.find('#do_unit_price').val(y.price_unit)
						  	$clone.find('#do_subtotal').val(parseFloat(y.price_unit) * parseInt(y.product_uom_qty))
		            	}else{
		            		if(y.comment){
	        				  	var $clone =  $('#table').find('tr.do_note_tr').clone(true).removeClass('d-none do_note_tr ').addClass('do_tr');
    					  		$clone.find('textarea.my_do_comment').val(y.comment)
		            		}
		            	}
					  	$('#table').find('table').append($clone);
						var option = '<option class="domenu_sel_option" value=' +  y.product_id +  '>' +  y.product_name + '</option>'
						$clone.find('select#selProduct_Template').append(option)
						$clone.find('select#selProduct_Template').attr("style", "pointer-events: none;");
				  		$clone.find('#selProduct_Template').removeClass('d-none')
				  		$clone.find('#selProduct').remove()
		            })
	    		}
	    	})
		})

		// -----------------------------------------CREATE SALE ORDER TEMPLATE

		$('#do_create_so_template').click(function (e) {
			var template_name = $('#set_template_name').val()
	 		var $do_tr = $('.do_tr')
			var data_list = []
			var create_so = true

	        $do_tr.each(function (x, y) {

				if ($(y).find('#selProduct').length == 1){
					var product =  $(y).find('#selProduct')
				}else{
					var product =  $(y).find('#selProduct_Template')
				}

				var product_value =  product.val()
				var quantity =  $(y).find('#do_qty')
				var quantity_value =  quantity.val()
				
				var comment =  $(y).find('textarea.my_do_comment')
				var comment_value =  comment.val()

				// create_qty = quantity
				if(product.length != 0 && comment.length == 0){
					if(product_value > 0 && quantity_value == 0){
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product Quantity!')
			   		    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
			   		    return false;
					}

					if(product_value == 0 && quantity_value == 0){
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product and Quantity!')
			   		    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
			   		    return false;
					}

					if(product_value == 0 && quantity_value != 0){
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product!')
					    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
					    return false;
					}

					if(product_value > 0 && quantity_value != 0 && template_name){
						var unit_price =  $(y).find('#do_unit_price').val()
						var data_dict  = {'product_id': parseInt(product_value) ,'product_uom_qty': parseInt(quantity_value)}
						data_list.push(data_dict)
					}else{
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Template Name!')
					    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
					    return false;
					}
				}
				if(product.length == 0 && comment.length != 0){
					if(comment_value){
						var comment = {'comment':comment_value}
						data_list.push(comment)
					}else{
						create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Note!')
					   setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
						return false;
					}
				}

        	})
        	if(data_list && create_so){
				$('#s_template_name').hide()
				$('#set_template_name').hide()
				$('#do_create_so_template').hide()
		    	ajax.jsonRpc('/create/so/template', 'call',{template_name,data_list}).then(function(val){
		    		if(val){
						$('.so_template_model').remove()
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_title').text('Successfully')
						$('.so_template_model').find('.do_modal_body').text('Confirm Add Template !')

			   		    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
		    		}
		    	})
        	}
        	
		});

		// ------------------------------REMOVE ROW IN DIRECT ORDER MENU ----------------------------
		
		$('.do_table-remove').click(function(){
			// var tr = $(this).parent().parent()
			var tr = $(this).closest('.do_tr');
			tr.remove()
		    setTimeout(function(){
				if(!$('.do_tr').length >= 1){
					$('#s_template_name').hide()
					$('#do_create_so_template').addClass('d-none')
					$('#set_template_name').addClass('d-none')
					$('.temp_lable_product').show()
				}
   		    },1000)
		});

		//---------------------------------------------------------------------------------------------------
		//-----------------------------------MY DIRECT ORDER ------------------------------------------------
		//---------------------------------------------------------------------------------------------------

		// ADD TABLE ROW

		$('#my_direct_clone_tr').click(function() {
			var test = $('#sales_order_table').find('tr.my_do_tr')
		  	var $clone =  $('#sales_order_table').find('tr.my_do_tr').clone(true).removeClass('d-none my_do_tr').addClass('my_do_common_tr');
		  	$('#details').find('#sales_order_table').append($clone);
		  	
		  	$clone.find("#selProduct").select2({
				placeholder: " ---Select--- ",
				multiple: false,
				// minimumInputLength: 1,
				ajax: {
					url: "/do/search/product",
					dataType: 'json',
					quietMillis: 250,
				  	data: function(term, page) {
				      	return {
				        	name: term,
				        };
	    			},
				    results: function(data, page) {
				     	return {results: data};
     		 	    },
				    cache: true
				},
				formatResult: function(element){
				   	return element.text;
				},
				formatSelection: function(element){
				   	return element.text;
				},
				escapeMarkup: function(m) {
				   	return m;
				}
			});

			mySelect($clone)
		});

		function mySelect(clone) {
		    setTimeout(function(){
				clone.find('#selProduct').on('change',function(){
					var select_val = $(this).val()
					var tr = $(this).closest('.my_do_common_tr');
			    	ajax.jsonRpc('/product/onchange/data', 'call',{'id':select_val}).then(function(val){
			    		if(val){
							var unit_price = $(tr).find('.my_quote_qty').text()
				    		$(tr).find('.unit_price').text(val.price)
				    		$(tr).find('.do_order_line_price_subtotal').text(parseFloat(val.price) * parseInt(unit_price))
			    		}
			    	})
				});	
		   	},1000);
		};

		// ------------------MY DO ADD NOTE ------------------------

		$('#my_do_note_tr').click(function() {
			var test = $('#sales_order_table').find('tr.my_do_note')
		  	var $clone =  $('#sales_order_table').find('tr.my_do_note').clone(true).removeClass('d-none my_do_note').addClass('my_do_common_tr');
		  	$('#details').find('#sales_order_table').append($clone);
		});

		// ----------------------ADD ITEM -----------------------

		$('#my_save_do_id').click(function() {
	 		// var $my_directdo_tr = $('.my_directdo_tr')
	 		var $my_directdo_tr = $('.my_do_common_tr')
			var data_list = []
			var my_create_so = true
            $my_directdo_tr.each(function (x, y) {
				var product =  $(y).find('#selProduct')
				var product_value =  product.val()
				var comment =  $(y).find('textarea.my_do_comment')
				var comment_value =  comment.val()
				var quantity =  $(y).find('.my_quote_qty')
				var quantity_value =  parseInt(quantity.text())
				
				if(product.length != 0  && comment.length == 0){
					if(product_value > 0 && quantity_value == 0){
						my_create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product Quantity!')
			   		    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
			   		    return false;
					}

					if(product_value == 0 && quantity_value == 0){
						my_create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product and Quantity!')
			   		    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
			   		    return false;
					}
					if(product_value == 0 && quantity_value != 0){
						my_create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Product!')
					    setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
					    return false;
					}
					if(product_value != 0 && quantity_value != 0){
						var data_dict  = {'product_id': parseInt(product_value) ,'product_uom_qty': parseInt(quantity_value)}
						data_list.push(data_dict)
					}
				}
				if(product.length == 0  && comment.length != 0){
					if(comment_value){
						var comment = {'comment':comment_value}
						data_list.push(comment)
					}else{
						my_create_so = false
						$('footer#bottom').before(bs_model)
						$('.so_template_model').find('.do_modal_body').text('Please Add Note!')
					   setTimeout(function(){
			   		    	$('.so_template_model').remove()
			   		    },2000)
						return false;
					}
				}
        	})

            if(data_list && my_create_so){
				var url = window.location.href.split('my/orders/')
				var order_id = url[1].split('?')[0]
		    	ajax.jsonRpc('/my/do/update', 'call',{data_list,order_id}).then(function(val){
		    		location.reload();
		    	})	
            }
		});

		$('.my_do_table_td').click(function() {
			var tr = $(this).parent().parent()
			tr.remove()
		})
		
		//REMOVE ORDER LINE IN MY DIRECT ORDER

		$('.my_do_table-remove').click(function() {
			var url = window.location.href.split('my/orders/')
			var order_id = url[1].split('?')[0]
			var tr = $(this).parent().parent()
			if ($(tr).find('#product_name').length >=1){
				var line = $(tr).find('#product_name').find('span')[0].dataset.oeId
			}else{
				var line = $(tr).find('span')[0].dataset.oeId
			}
		  	ajax.jsonRpc('/my/delete/line', 'call',{line}).then(function(val){
	    		if(val){
	    			tr.remove()
	    		}
	    	})	
		});

		// ORDER LINE EDITABLE IN MY DIRECT ORDER

		if($('.o_portal_sidebar').length == 1){
			if($('.oe_currency_value').parent()){
				if($('.oe_currency_value').parent()[0].dataset){
					var so_id = $('.oe_currency_value').parent()[0].dataset.oeId	
			    	ajax.jsonRpc('/my/do/update', 'call',{so_id}).then(function(val){
			    		if(val){

		    				if($('.sale_tbody').find('td#product_name').length > 0){
		    					var qty_td =  $('.my_order_qty').attr('contenteditable','true')
		    				}
			    		}
	    			});
				}
			}
		}

		// -------------------------UPDATE PRODUCT QTY BACKEND AND FRONT END IN ORDER LINE -------------------

	    setTimeout(function(){ 
			$('.my_order_qty').on('propertychange input', function (e) {
				var self = this
				var unit_price = parseFloat($(self).next().text())
				var unit = $(self).next()
				var qty_unit = $(self).text()

				if(qty_unit >= 1){
					var total_price = qty_unit *  unit_price
	 				var so_line = $(unit).children()[0].dataset.oeId
					$(self).parent().find('.oe_currency_value').text(total_price)
			    	ajax.jsonRpc('/my/update/so_line', 'call',{so_line,qty_unit}).then(function(val){

			    	})
				}
			})
		},500)

		$('#unit_qty').on('DOMSubtreeModified', function (e){
			var self = this
			var unit_price = parseFloat($(self).next().text())
			var qty_unit = parseInt($(self).text())
			if(qty_unit >= 1){
				var total_price = qty_unit *  unit_price
				$(self).parent().find('.do_order_line_price_subtotal').text(total_price)
			}
		})

		// ----------------------------CONFIRM SALE ORDER -----------------------------

		$('#my_confirm_order').click(function(){
			var self = this;
 			if($('.oe_currency_value').parent()){
				if($('.oe_currency_value').parent()[0].dataset){
					var so_id = $('.oe_currency_value').parent()[0].dataset.oeId	
			    	ajax.jsonRpc('/my/confirm/so', 'call',{so_id}).then(function(val){
			    		if(val){
			    			$('.confirm_order_model').remove()
							$('footer#bottom').before(bs_model)
							$('.so_template_model').find('.do_modal_title').text('Successfully')
							$('.so_template_model').find('.do_modal_body').text('Confirm Order!')
				   		    setTimeout(function(){
				   		    	location.reload()
				   		    },1000) 
			    		}
	    			});
				}
			}
		})

	});
})