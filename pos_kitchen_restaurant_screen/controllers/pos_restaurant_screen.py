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
# import os.path as os_path
import threading
import logging
_logger = logging.getLogger(__name__)
import odoo.addons.pos_kitchen_screen.controllers.pos_kitchen_screen as kitchen


# class PosKitchenRestaurantScreen(kitchen.KitchenScreenBase):


    # def get_queue_orders_data(self,config_id):
    #     pos_screen_data = request.env['pos.kitchen.screen.config'].sudo().browse(config_id)
    #     pos_orders = False
    #     restaurant_orders = False
    #     for config in pos_screen_data.pos_config_ids:
    #         if config.module_pos_restaurant:
    #             restaurant_orders = request.env['pos.kitchen.order'].sudo().search([('order_progress','in',['pending','partially_done']),('date_order','>=',datetime.date.today()),('config_id','in',pos_screen_data.pos_config_ids.ids)],order="id asc")
    #         else:
    #             pos_orders = request.env['pos.order'].sudo().search([('table_id','=',False),('order_progress','in',['pending','partially_done']),('date_order','>=',datetime.date.today()),('config_id','in',pos_screen_data.pos_config_ids.ids)],order="id asc")
    #     order_data = self.get_data_from_orders(True,pos_screen_data,pos_orders=pos_orders,restaurant_orders= restaurant_orders)
    #     return order_data
