# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo.http import request,Response
from odoo import http
import pytz
import jinja2
import datetime
import json
import os.path as os_path
import threading
import logging
_logger = logging.getLogger(__name__)

class KitchenScreenBase(http.Controller):

    @http.route('/pos/kitchen/<int:id>/screen', type='http', auth='none')
    def display_kitchen_screen(self,**kw):
        try:
            config_id = kw.get('id')
            order_data = self.get_queue_orders_data(config_id)
            return request.render('pos_kitchen_screen.pos_kitchen_screen_template',qcontext={'data':order_data})
        except Exception as e:
            _logger.info("*************Exception************:%r",e)



    @http.route('/pos/<int:id>/order/list/', type='json', auth='none')
    def order_list_screen(self,**kw):
        #_logger.info('/order/list/----%r',kw)
        pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(kw.get('id'))
        pos_orders = request.env['pos.order'].sudo()
        restaurant_orders = request.env['pos.kitchen.order'].sudo()
        if  'pos' in kw.get('order_type'):
            pos_orders += request.env['pos.order'].sudo().browse(kw.get("order_id"))
        else:
            restaurant_orders += request.env['pos.kitchen.order'].sudo().browse(kw.get("order_id"))
        order_data = self.get_data_from_orders(True,pos_screen_data,pos_orders=pos_orders,restaurant_orders=restaurant_orders)
        return order_data


    def get_data_from_orders(self,isUpdateTime,pos_screen_data,**kwargs):
        order_data = {
            'last_order_time':False,
            'order_data':[],
            'change_order_data':[]

        }
        if (kwargs.get('pos_orders') and len(kwargs.get('pos_orders')) ) or (kwargs.get('restaurant_orders') and len(kwargs.get('restaurant_orders')) or pos_screen_data.is_changed):
            orders_list = []
            if kwargs.get('pos_orders'):
                for order in kwargs.get('pos_orders'):
                    self.extract_order_data(order,orders_list,pos_screen_data)
                    if len(orders_list):
                        orders_list[-1]['order_type'] = 'pos'
            if kwargs.get('restaurant_orders'):
                for order in kwargs.get('restaurant_orders'):
                    self.extract_order_data(order,orders_list,pos_screen_data)
                    if len(orders_list):
                        orders_list[-1]['order_type'] = 'restaurant'
                        orders_list[-1]['floor_id'] = order.floor_id.name
                        orders_list[-1]['table_id'] = order.table_id.name
            sorted(orders_list,key=lambda l : l.get('order_date'))
            order_data.update({
                'order_data':orders_list
            })
            _logger.info("*************screne changed********%r",pos_screen_data.is_changed)
            if pos_screen_data.is_changed:
                changed_restaurant_orders = request.env['pos.kitchen.order'].sudo().search([('order_progress','in',['cancel','pending','partially_done']),('date_order','>=',datetime.date.today()),('config_id','in',pos_screen_data.pos_config_ids.ids),('is_changed','=',True)],order="id asc")
                for order in changed_restaurant_orders:
                    vals={'id':order.id,'state':order.order_progress}
                    product_category_wise = {}
                    if order.order_progress in ['pending','partially_done']:
                        for line in order.lines:
                            if not line.is_orderline_done:
                                count = 0
                                for categ in line.product_id.pos_categ_id:
                                    if categ in pos_screen_data.pos_category_ids and not count:
                                        count += 1
                                        line_vals = {}
                                        line_vals['note'] = hasattr(line,'note') and line.note or ''
                                        line_vals['display_name'] = line.display_name
                                        line_vals['id'] = line.id
                                        line_vals['qty_added'] = line.qty_added
                                        line_vals['state'] = line.state
                                        line_vals['qty_removed'] = line.qty_removed
                                        line_vals['order_id'] = [line.order_id.id, line.order_id.name]
                                        line_vals['done_line'] = "/pos/"+str(line.id)+"/done/orderline"
                                        line_vals['screen_config'] = pos_screen_data.id
                                        line_vals['product_id'] = [line.product_id.id,line.full_product_name or line.product_id.name]
                                    #    _logger.info('-------full_name-00--%r',line.full_product_name)
                                        line_vals['qty'] = line.qty
                                        categ_id = categ.name+'-'+str(categ.id)
                                        if categ_id not in product_category_wise:
                                            product_category_wise[categ_id] = {line.id:line_vals}
                                        else:
                                            product_category_wise[categ_id].update({line.id:line_vals})

                        vals['product_category_wise'] = product_category_wise
                    order_data['change_order_data'].append(vals)
                    order.sudo().write({'is_changed':False})

                pos_screen_data.sudo().write({'is_changed':False})
        return order_data

    def extract_order_data(self,order,orders_list,pos_screen_data):

        config_id = order.config_id
        pos_screen_data = pos_screen_data
        is_allowed_order = True
        has_category_product = []
        if len(pos_screen_data.pos_category_ids.ids):
            for line in order.lines:
                if not line.is_orderline_done:
                    for cat in line.product_id.pos_categ_id:
                        if cat.id in pos_screen_data.pos_category_ids.ids:
                            has_category_product.append(line.product_id)
            if len(has_category_product) == 0:
                is_allowed_order = False
        if is_allowed_order:
            vals = {}
            vals['lines'] = []
            vals['name'] = order.name
            vals['amount_total'] = order.amount_total
            vals['pos_name'] = order.config_id.name
            vals['pos_reference'] = order.pos_reference
            vals['cancel_order'] = "/pos/"+str(order.id)+"/cancel/order"
            vals['confirm_order'] = "/pos/"+str(order.id)+"/confirm/order"
            vals['done_order'] = "/pos/"+str(order.id)+"/done/order"
            vals['cook_order'] = "/pos/"+str(order.id)+"/cook/order"
            vals['kitchen_order_name'] = order.kitchen_order_name
            order_date = order.date_order
            if request.env.context.get('tz'):
                user_tz = pytz.timezone(request.env.context.get('tz'))
                order_date = pytz.utc.localize(order.date_order).astimezone(user_tz)
            vals['order_date'] = order_date.strftime("%H:%M:%S")
            vals['order_progress'] = order.order_progress
            vals['orders_on_grid'] = int(pos_screen_data.orders_on_grid)
            if int(pos_screen_data.orders_on_grid) % 3 == 0:
                vals['grid_class'] = "col-md-4 order-new"
            elif int(pos_screen_data.orders_on_grid) % 2 == 0:
                vals['grid_class'] = "col-md-6 order-new"
            else:
                vals['grid_class'] = "col-md-4 order-new"
            if order.partner_id:
                vals['partner_id'] = [order.partner_id.id, order.partner_id.name]
            else:
                vals['partner_id'] = False
            vals['id'] = order.id
            product_category_wise = {}
            #_logger.info("******order.lines********:%r",order.lines)
            for line in order.lines:
                if not line.is_orderline_done:
                    count = 0
                    # if line.product_id.use_as_modifier:
                    #     self.accumulate_line_data(line,vals,pos_screen_data,count,config_id,product_category_wise,False)
                    # else:
                    for categ in line.product_id.pos_categ_id:
                        self.accumulate_line_data(line,vals,pos_screen_data,count,config_id,product_category_wise,categ)
            vals['total_items'] = len(vals['lines'])
            orders_list.append(vals)

    def accumulate_line_data(self,line,vals,pos_screen_data,count,config_id,product_category_wise,categ):
        # _logger.info("*******8line.product_id.use_as_modifier****:%r",line.product_id.use_as_modifier)
        if categ and categ in pos_screen_data.pos_category_ids and not count:
            #_logger.info("*********inn**********")
            count += 1
            line_vals = {}
            line_vals['note'] = hasattr(line,'note') and line.note or ''
            line_vals['display_name'] = line.display_name
            line_vals['id'] = line.id
            line_vals['state'] = line.state
            line_vals['done_line'] = "/pos/"+str(line.id)+"/done/orderline"
            line_vals['order_id'] = [line.order_id.id, line.order_id.name]
            line_vals['screen_config'] = pos_screen_data.id
            # if config_id.module_pos_restaurant and line.qty_added:
            if hasattr(config_id,'order_action') and config_id.order_action == 'order_button' and line.qty_added:

                line_vals['qty_added'] = line.qty_added
            # if config_id.module_pos_restaurant and line.qty_removed:
            if hasattr(config_id,'order_action') and config_id.order_action == 'order_button' and line.qty_removed:
                line_vals['qty_removed'] = line.qty_removed
            product = line.read(['product_id'])
            if len(product):
                line_vals['product_id'] = list(product[0].get('product_id'))
                line_vals['product_id'][1] = line.full_product_name or line_vals['product_id'][1]
                if len(line_vals['product_id'][1].split(']')) == 2:
                    line_vals['product_id'][1] = line.full_product_name or line_vals['product_id'][1].split(']')[1]
            else:
                line_vals['product_id'] = [line.product_id.id,line.full_product_name or line.product_id.name]
            #_logger.info('-------full_name---%r',(line_vals.get('full_product_name',''),line.full_product_name))
            line_vals['qty'] = line.qty
            if categ:
                categ_id = categ.name+'-'+str(categ.id)
                if categ_id not in product_category_wise:
                    product_category_wise[categ_id] = {line.id:line_vals}
                else:
                    product_category_wise[categ_id].update({line.id:line_vals})
            else:
                categ_id = "General"+'-'+str(0)
                if categ_id not in product_category_wise:
                    product_category_wise[categ_id] = {line.id:line_vals}
                else:
                    product_category_wise[categ_id].update({line.id:line_vals})

            vals['lines'].append(line_vals)
            vals['product_category_wise'] = product_category_wise

    def get_queue_orders_data(self,config_id):
        pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(config_id)
        pos_orders = request.env['pos.order'].sudo()
        restaurant_orders = request.env['pos.kitchen.order'].sudo()
        for config in pos_screen_data.pos_config_ids:
            # if config.module_pos_restaurant:
            #_logger.info("-----------%r",config)
            #_logger.info("-----------%r",hasattr(config,'order_action'))
            if hasattr(config,'order_action') and config.order_action == 'order_button':
                orders = request.env['pos.kitchen.order'].sudo().search([('order_progress','in',['pending','partially_done']),('date_order','>=',datetime.date.today()),('config_id','in',pos_screen_data.pos_config_ids.ids)],order="id asc")
                #_logger.info("-----------%r",orders)
                for order in orders:
                    if order.id not in restaurant_orders.ids:
                        restaurant_orders += order
            else:
                orders = request.env['pos.order'].sudo().search([('order_progress','in',['pending','partially_done']),('date_order','>=',datetime.date.today()),('config_id','in',pos_screen_data.pos_config_ids.ids)],order="id asc")
            #    _logger.info("--------else---%r",orders)
                for order in orders:
                    if order.id not in pos_orders.ids:
                        pos_orders += order
        #_logger.info("-----------%r",orders)
        order_data = self.get_data_from_orders(True,pos_screen_data,pos_orders=pos_orders,restaurant_orders= restaurant_orders)
        return order_data

    @http.route('/pos/kitchen/<int:id>/data', type='json', auth='none')
    def get_kitchen_screen(self,**kw):
        config_id = kw.get('id')
        order_data = self.get_queue_orders_data(config_id)
    #    _logger.info('-----data--%r',len(order_data['order_data']))
        return order_data





    @http.route('/pos/<int:id>/new/orders',  type="json", auth="none",cors='*')
    def new_orders(self,**kw):
        updateTime = kw.get('updateTime')
        existing_orders = kw.get('existing_orders')
        pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(kw.get('id'))
        domain = [('kitchen_order_name','!=',False),('order_progress','!=',False),('order_progress','=','new'),('id','not in',existing_orders),('date_order', '>=', datetime.date.today()),('config_id','in',pos_screen_data.pos_config_ids.ids)]
        pos_orders = request.env['pos.order'].sudo()
        restaurant_orders = request.env['pos.kitchen.order'].sudo()
        for config in pos_screen_data.pos_config_ids:
            if hasattr(config,'order_action') and config.order_action == 'order_button':
                orders = request.env['pos.kitchen.order'].sudo().search(domain,order="id asc")
                for order in orders:
                    if order.id not in restaurant_orders.ids:
                            restaurant_orders +=order
            else:
                orders = request.env['pos.order'].sudo().search(domain,order="id asc")
                for order in orders:
                    if order.id not in pos_orders.ids:
                            pos_orders +=order
        order_data = self.get_data_from_orders(True,pos_screen_data,pos_orders=pos_orders,restaurant_orders=restaurant_orders)

        #config_id = kw.get('id')
        #order_existing_data = self.get_queue_orders_data(config_id)
        #_logger.info('-------%r',(id,kw))
        #order_data['order_existing_data']=order_existing_data
        return order_data


    @http.route('/pos/<int:id>/order/show/',  type="json", auth="none",cors='*')
    def show_new_order(self,**kw):
        pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(kw.get('id'))
        pos_orders = request.env['pos.order'].sudo()
        restaurant_orders = request.env['pos.kitchen.order'].sudo()
        if kw.get('order_type') == 'pos':
            pos_orders += request.env['pos.order'].sudo().browse(kw.get("order_id"))
        else:
            restaurant_orders += request.env['pos.kitchen.order'].sudo().browse(kw.get("order_id"))
        order_data = self.get_data_from_orders(True,pos_screen_data,pos_orders=pos_orders,restaurant_orders=restaurant_orders)
        return order_data




    @http.route('/pos/<int:id>/process/orders/',  type="json", auth="none",cors='*')
    def append_process_order(self,**kw):
        pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(kw.get('id'))
        pos_orders = request.env['pos.order'].sudo()
        restaurant_orders = request.env['pos.kitchen.order'].sudo()
        if kw.get('order_type') == 'pos':
            pos_orders += request.env['pos.order'].sudo().browse(kw.get("order_id"))
        else:
            restaurant_orders += request.env['pos.kitchen.order'].sudo().browse(kw.get("order_id"))
        order_data = self.get_data_from_orders(True,pos_screen_data,pos_orders=pos_orders,restaurant_orders=restaurant_orders)
        return order_data


    @http.route('/pos/<int:id>/cancel/order',type='http', auth='none', cors='*', csrf=False, save_session=False)
    def cancel_order(self,**kw):
        order = False
        if kw.get('order_type') == 'pos':
            order = request.env['pos.order'].sudo().browse(kw.get('id'))
        else:
            order = request.env['pos.kitchen.order'].sudo().browse(kw.get('id'))
        vals = {
            'order_progress':'cancel',
            'is_state_updated':True
        }
        if kw.get('cancel-option') == 'out_of_stock':
            ids = []
            raw_dict = kw.copy()
            del raw_dict['cancel_reason']
            del raw_dict['cancellation_type']
            del raw_dict['cancel-option']
            del raw_dict['id']
            del raw_dict['order_type']
            ids = [int(index) for index in raw_dict.keys()]
            vals.update({
                'out_of_stock_products':[(6,0,ids)]
            })
        else:
            vals.update({
                'cancellation_reason':kw.get('cancel_reason')
            })
        _logger.info("*********order*****%r**********************vals******%r",order,vals)
        order.sudo().write(vals)

    @http.route('/pos/<int:id>/confirm/order',type='json', auth='none', cors='*', csrf=False, save_session=False)
    def confirm_order(self,**kw):
        order = False
        _logger.info("**********Confirm Order*******%r",kw)
        if kw.get('order_type') == 'pos':
            order = request.env['pos.order'].sudo().browse(kw.get('id'))
            config = order.session_id.config_id.id
        else:
            order = request.env['pos.kitchen.order'].sudo().browse(kw.get('id'))
            config = order.config_id.id
        screen = request.env['pos.kitchen.screen.config'].sudo().search([])
        sc_av=[]
        for  i in screen:
            if config in i.pos_config_ids.ids:
                sc_av.append(i)
        cat_av=[]
        for i in sc_av:
            cat_av+=i.pos_category_ids.ids
        #_logger.info('/confirm---%r',(cat_av,sc_av))
        for line in order.lines:
            if not line.is_orderline_done:
                for cat in line.product_id.pos_categ_id:
                    if cat.id in cat_av:
                        line.write({'state':'in_process'})
        order.sudo().write({
            'order_progress' : 'pending',
            'is_state_updated':True
        })

    @http.route('/pos/<int:id>/done/order',type='json', auth='none', cors='*', csrf=False, save_session=False)
    def done_order(self,**kw):
        order = False
        has_category_product = []
        #_logger.info('--------/order--%r',kw)
        pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(int(kw.get('screen_config')))
        if kw.get('order_type') == 'pos':
            order = request.env['pos.order'].sudo().browse(kw.get('id'))
        else:
            order = request.env['pos.kitchen.order'].sudo().browse(kw.get('id'))
        for line in order.lines:
            if line.state=='in_process':
                for cat in line.product_id.pos_categ_id:
                    if cat.id in pos_screen_data.pos_category_ids.ids:
                        line.sudo().write({'state' : 'done'})
                        has_category_product.append(line.product_id)
        order_progress='done'
        for line in order.lines:
            if line.state=='in_process':
                order_progress='partially_done'
        order.sudo().write({
            'order_progress' : order_progress,
            'is_state_updated':True
        })
        #for line in order.lines:
        #    line.is_orderline_done = True
        #    line.state = 'done'

    @http.route('/pos/<int:id>/cook/order',type='http', auth='none', cors='*', csrf=False, save_session=False)
    def cook_order(self,**kw):
        order = False
        if kw.get('order_type') == 'pos':
            order = request.env['pos.order'].sudo().browse(kw.get('id'))
        else:
            order = request.env['pos.kitchen.order'].sudo().browse(kw.get('id'))
        order.sudo().write({
            'order_progress' : 'partially_done',
            'is_state_updated':True
        })


    @http.route('/pos/<int:id>/done/orderline',type='json', auth='none', cors='*', csrf=False, save_session=False)
    def done_orderline(self,**kw):
        line_changed = False
        has_category_product = []
        pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(int(kw.get('screen_config')))
        if kw.get('order_type') == 'pos':
            line_changed = request.env['pos.order.line'].sudo().browse(kw.get('id'))
            if len(pos_screen_data.pos_category_ids.ids):
                #has_category_product = [line.product_id for line in line_changed.order_id.lines if line.product_id.pos_categ_id.id in pos_screen_data.pos_category_ids.ids]
                has_category_product = [line.product_id for line in line_changed.order_id.lines if line.state =='in_process' or line.state=='done' ]
        else:
            line_changed = request.env['pos.kitchen.orderline'].sudo().browse(kw.get('id'))
            for line in line_changed.order_id.lines:
                if line.state=='in_process' or line.state=='done':
                #    for cat in line.product_id.pos_categ_id:
                #        if cat.id in pos_screen_data.pos_category_ids.ids:
                    has_category_product.append(line.product_id)

        line_changed.sudo().write({
            'state' : 'done'
        })
        order_progress = 'partially_done'
        count = 0
        for line in line_changed.order_id.lines:
            if line.state == 'done':
                count += 1
        #_logger.info('/orderline--%r',(count,has_category_product))
        if count == len(has_category_product):
            order_progress = 'done'

        line_changed.order_id.sudo().write({
            'order_progress' : order_progress,
            'is_state_updated':True
        })
    @http.route(['/pos/<int:id>/today/orders/'], type='json', auth="user", methods=['POST'])
    def page_tokens(self, **kw):
        posOrderModel = request.env['pos.order']
        pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(kw.get('id'))
        domain = [('order_progress', '=', 'in_process'), ('date_order', '>=', datetime.date.today()),('config_id','in',pos_screen_data.pos_config_ids.ids)]
        orders = posOrderModel.search(domain, limit=2, offset=kw.get('offset'), order="id asc")
        order_data = self.get_data_from_orders(orders,False,pos_screen_data)
        return order_data
