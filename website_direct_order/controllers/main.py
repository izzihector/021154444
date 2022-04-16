# -*- coding: utf-8 -*-
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import json


class DirectOrder(http.Controller):

    def _get_pricelist_context(self):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        return pricelist_context, pricelist

    @http.route('/check/user/group', auth='public' , type='json' , website=True)
    def check_user_group(self):
        user_id = request.env['res.users'].browse(request.env.context.get('uid'))
        group = user_id.has_group('website_direct_order.manage_direct_order_group_admin')
        pricelist = request.website.get_current_pricelist()
        price_symbol = pricelist.currency_id.symbol
        value = {'group' :group ,'price_symbol':price_symbol}
        return value

    @http.route(['/direct/order'], type='http', auth='user', website=True)
    def direct_sale_order(self):

        partner = request.env.user.partner_id
        order_template = request.env['sale.order.template'].sudo().search([('partner_id','=', partner.id)])

        return request.render("website_direct_order.direct_order_table", {'order_template':order_template})

    @http.route('/do/search/product',  type='http', auth='public', cors='*', csrf=False, save_session=False)
    def search_product(self,**data):
        product_ids = []
        if 'name' in data:
            pro_name = data['name']
            if pro_name:
                prods_ids = request.env['product.product'].sudo().search(['|','|',('default_code','ilike',pro_name),('name','ilike',pro_name),('barcode','ilike',pro_name),('is_published','=', True)],limit=10)
                for product in prods_ids:
                    product_ids.append({'id':product.id,'text': product.display_name})

            else:
                prods_ids = request.env['product.product'].sudo().search([('is_published','=', True)],limit=10)
                for product in prods_ids:
                    product_ids.append({'id':product.id,'text': product.display_name})


        else:
            prods_ids = request.env['product.product'].sudo().search([('is_published','=', True)],limit=10)
            for product in prods_ids:
                product_ids.append({'id':product.id,'text': product.display_name})

        product_ids = json.dumps(product_ids)
        return product_ids

    @http.route('/do/create', auth='public' , type='json' , website=True)
    def do_create(self, **data):    
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        if 'data_list' in data:
            data_dic = data['data_list']
            # data_dic = data['data_list']
            if data_dic:
                order = request.env['sale.order']
                order_line = request.env['sale.order.line']
                partner = request.env.user.partner_id
                order = order.create({
                        'partner_id':partner.id,    
                        'is_direct_order':True,
                    })
                if order:
                    for data in data_dic:
                        if 'comment' in data:
                            order_line.create({
                                'order_id': order.id,
                                'display_type': 'line_note',
                                'name':data['comment'],
                                })
                        else:
                            order_line.create({
                                'order_id': order.id,
                                'product_id':data['product_id'],
                                'product_uom_qty':data['product_uom_qty']
                                })

                    my_do_url = base_url + '/my/orders/' + str(order.id)
                    return my_do_url
        else:
            return False

    @http.route('/create/so/template', auth='public' , type='json' , website=True)
    def create_so_temlate(self , ** data):
        env = request.env
        so_template_obj = env['sale.order.template']
        so_template_line_obj = env['sale.order.template.line']
        pricelist_context, pl = self._get_pricelist_context()
        if data['template_name']:
            so_template_id = so_template_obj.create({'name':data['template_name'],'partner_id':request.env.user.partner_id.id})

            if so_template_id:
                line_data = data['data_list']
                for data in line_data:
                    if not 'comment' in data and data.get('product_id') !=0 :
                        product = request.env['product.product'].browse(data.get('product_id'))
                        price = round(env['product.product'].with_context(pricelist_context, display_default_code=False).browse(product.id)._get_combination_info_variant()['price'],2),
                        main_price = str(price).replace("(",'').replace(',','').replace(')','')
                        description = product.display_name
                        so_template_line_id = so_template_line_obj.sudo().create({'sale_order_template_id':so_template_id.id, 
                                                                            'product_id':data.get('product_id'),
                                                                            'name':description,
                                                                            'product_uom_qty':data.get('product_uom_qty'),
                                                                            'product_uom_id':product.uom_id.id,
                                                                            }) 
                    else:
                        so_template_line_id = so_template_line_obj.sudo().create({'sale_order_template_id':so_template_id.id, 
                                                    'name':data['comment'],
                                                    'display_type':'line_note',
                                                    })
            
            return True
        return False

    @http.route('/so/template', auth='public' , type='json' , website=True)
    def my_so_template(self,**data):
        if 'so_template' in data:
            if data['so_template']:
                data_list = []
                pricelist_context, pl = self._get_pricelist_context()
                partner = request.env.user.partner_id.id
                order_template = request.env['sale.order.template'].sudo().search([('id','=',data['so_template'])])
                
                if order_template:
                    for line in order_template.sale_order_template_line_ids:
                        if line.display_type == 'line_note':
                            line = { 'comment':line.name}
                            data_list.append(line)
                        else:
                            price = round(request.env['product.product'].with_context(pricelist_context, display_default_code=False).browse(line.product_id.id)._get_combination_info_variant()['price'],2),
                            if not line.product_id.default_code:
                                line = { 'product_name':line.product_id.name ,
                                        'product_id':line.product_id.id,
                                        'product_uom_qty':line.product_uom_qty,
                                        'price_unit':price}
                            else:
                               line = { 'product_name':line.product_id.display_name,
                                    'product_id':line.product_id.id,
                                    'product_uom_qty':line.product_uom_qty,
                                    'price_unit':price}

                            data_list.append(line)
                    if data_list:
                        return data_list
        return False

    @http.route('/product/onchange/data', auth='public' , type='json' , website=True)
    def product_data(self, **pro_id):

        if 'id' in pro_id:
            if pro_id['id']:
                product_ids = request.env['product.product'].browse(int(pro_id['id']))
                value = {'price':round(product_ids._get_combination_info_variant()['price'],2)}
                return value
            else:
                return False

    @http.route('/my/delete/line', auth='public' , type='json' , website=True)
    def do_delete(self, **data):

        if 'line' in data:
            request.env['sale.order.line'].sudo().browse(int(data['line'])).unlink()
            return True
        else:
            return False


    @http.route('/my/do/update', auth='public' , type='json' , website=True)
    def my_do_create(self, **data):
        if 'data_list' in data:
            data_dic = data['data_list']
            order_line = request.env['sale.order.line']
            if 'order_id' in data:
                order = request.env['sale.order'].browse(int(data['order_id']))
                if order:
                    for data in data_dic:
                        
                        if 'comment' in data:
                            order_line.create({
                                'order_id': order.id,
                                'name':data['comment'],
                                'display_type': 'line_note',
                                })
                        else:
                            if data['product_id']:
                                product = request.env['product.product'].browse(data['product_id'])
                                description = product.display_name
                            order_line.create({
                                'order_id': order.id,
                                'name':description,
                                'product_id':data['product_id'],
                                'product_uom_qty':data['product_uom_qty']
                                })
                return True
        if 'so_id' in data:
            order = request.env['sale.order'].search([('id','=', data['so_id']),('state','=','draft')])
            if order:
                return True
    
    @http.route('/my/update/so_line', auth='public' , type='json' , website=True)
    def my_update_so_line(self, **data):
        if 'so_line' in data:
            so_id = request.env['sale.order.line'].sudo().browse(int(data['so_line']))
            if data['qty_unit']:
                so_id.write({'product_uom_qty':data['qty_unit']})
        return True
    
    @http.route('/my/confirm/so', auth='public' , type='json' , website=True)
    def confirm_sale_order(self, **data):
        if 'so_id' in data:
            so_id = data['so_id']
            if so_id:
                order = request.env['sale.order'].browse(int(so_id))
                order.write({'state':'done'}) 
            return True


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        direct_order_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft','done']),
            ('is_direct_order','=', True)

        ])
        values.update({
            'direct_order_count': direct_order_count,
        })
        return values

    @http.route(['/my/direct/order', '/my/direct/order/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_do(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
 
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft','done']),
            ('is_direct_order','=', True)
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/direct/order",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_direct_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'direct_orders': orders.sudo(),
            'page_name': 'direct_order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/direct/order',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_direct_order.portal_my_direct_orders", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done']),
            ('is_direct_order','!=', True),
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_orders", values)