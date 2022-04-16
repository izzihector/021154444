# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
#################################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class LoyalityCategory(models.Model):
    _name='loyalty.category'
    category_id = fields.Many2one('pos.category', string='POS Category', required = True)
    wk_point_for_loyalty = fields.Integer(string='Loyalty Points', help="How many loyalty points are given to the customer by product sold under this category.")
    loyalty_id = fields.Many2one('loyalty.management', required = True)

    @api.constrains('loyalty_id', 'category_id','wk_point_for_loyalty')
    def check_category_loyalty_points(self):
        for record in self:
            if record.category_id in [rec.category_id for rec in self.search([('loyalty_id','=',record.loyalty_id.id)]) if rec.id!=record.id]:
                raise ValidationError('Category should be unique !')
            elif record.wk_point_for_loyalty<0:
                raise ValidationError('Loyalty points can not be negative !')



class PosCategory(models.Model):
    _inherit = 'pos.category'

    wk_point_for_loyalty = fields.Integer(string='Loyalty Points', readonly = True, help="How many loyalty points are given to the customer by product sold under this category.")

    @api.constrains('wk_point_for_loyalty')
    def set_point_for_loyalty_for_child(self):
        for self_obj in self:
            categories_objs = self_obj.search([])
            for obj in categories_objs:
                if obj.parent_id.id == self_obj.id:
                    if  obj.wk_point_for_loyalty == 0:
                        obj.wk_point_for_loyalty = self_obj.wk_point_for_loyalty

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wk_point_for_loyalty = fields.Integer(related='pos_categ_id.wk_point_for_loyalty', string='Loyalty Points',
                                          help="How many loyalty points are given to the customer by product sold.", readonly=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wk_loyalty_points = fields.Integer(string='Loyalty Points', compute="calc_loyalty_points", help='The loyalty points the user won as part of a Loyalty Program')

    def calc_loyalty_points(self):
        for partner in self:
            loyalty_history_data = self.env['pos.loyalty.history'].search([('customer_id','=',partner.id)])
            partner_loyalty_points = 0
            for entry in loyalty_history_data:
                if entry.tx_type == 'credit':
                    partner_loyalty_points += entry.tx_points
                else:
                    partner_loyalty_points -= entry.tx_points
            partner.wk_loyalty_points = partner_loyalty_points
        

class LoyaltyManagement(models.Model):
    _name = 'loyalty.management'
    _description = "POS loyalty Configration"

    def _default_loyalty_product(self):
        ir_model_data = self.env['ir.model.data']
        product_id = False
        try:
            product_id = ir_model_data.get_object_reference('pos_loyalty_management', 'wk_loyalty_product_id')[1]
        except ValueError:
            product_id = False
        return product_id

    name = fields.Char(string='Name', size=100, default=lambda self: _('/'))
    start_date = fields.Datetime(string='Start Date', default=fields.Datetime.now)
    end_date = fields.Datetime(string='End Date')
    redeem_rule_list = fields.Many2many('redeem.rule.list', 'rule11', 'rule22', 'rule33', string='Redemption Rule List')
    minimum_purchase = fields.Monetary(string='Minimum Purchase amount for which the points can be awarded', help="Minimum Purchase amount for which the points can be awarded.")
    config_active = fields.Boolean(string='Active', default=True)
    points = fields.Integer(string='Points')
    purchase = fields.Float(string='Purchase')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency of your Company.", default=lambda self: self.env.user.company_id.currency_id.id)

    loyality_product_id = fields.Many2one('product.product', string='Loyalty Product', domain=[('sale_ok', '=', True), ('available_in_pos', '=', True)], help="This Product is used as a Loyalty Product.", default=_default_loyalty_product)

    loyalty_base = fields.Selection([('amount', 'Purchase Amount'),
                                     ('category', 'POS Product Categories')
                                     ], string='On the Basis', required=True, default='category')

    categories_ids = fields.One2many('loyalty.category','loyalty_id')
    redeem_type = fields.Selection([('partial','Partially Redeem'),('full','Fully Redeem')], string = 'Redeem Type', default = 'partial', required = True)
    minimum_points = fields.Integer('Min. Points to Redeem', help = 'Minimum points required to redeem')
    message = fields.Text(default = 'You are fully redeeming your points. Rest points will be collapsed. Do you want to continue?', help = 'Message displayed on Fully redeem.')

    @api.model
    def create(self, vals):
        if vals.get('config_active'):
            if len(self.search([('config_active', '=', True)])) >= 1:
                raise UserError(_("Sorry, Only one active configuration is allowed."))
        if vals:
            redeem_rule_list_ids = vals.get('redeem_rule_list')
            if redeem_rule_list_ids:
                redeem_list = redeem_rule_list_ids[0][2]
                redeem_rule_objs = self.redeem_rule_list.search([('id','in',redeem_list)])
                for index in range(0,len(redeem_list)-1):
                    for sibling_index in range(index+1,len(redeem_list)):
                        points_ub = redeem_rule_objs[index].points_to
                        points_lb = redeem_rule_objs[index].points_from
                        sibling_ub = redeem_rule_objs[sibling_index].points_to
                        sibling_lb = redeem_rule_objs[sibling_index].points_from
                        if((points_lb >= sibling_lb and points_lb < sibling_ub) or (points_ub > sibling_lb and points_ub <= sibling_ub)) :
                            raise ValidationError("There is some overlapping in Redemption Rule List Range. Please check and re-assign range again.")
                        elif((sibling_lb >= points_lb and sibling_lb < points_ub) or (sibling_ub > points_lb and sibling_ub <= points_ub)):
                           raise ValidationError("There is some overlapping in Redemption Rule List Range. Please check and assig points range again.")
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('loyalty.management')
        res = super(LoyaltyManagement, self).create(vals)
        if res.config_active:
            for categ in self.env['pos.category'].search([]):
                loyal_categ = self.env['loyalty.category'].search([('category_id','=',categ.id),('loyalty_id','=',res.id)])
                if loyal_categ:
                    categ.write({'wk_point_for_loyalty' : loyal_categ.wk_point_for_loyalty})
                else:
                    categ.write({'wk_point_for_loyalty' : 0})
        return res

    @api.constrains('start_date','end_date')
    def date_validation_check(self):
        if self.start_date:
            if self.end_date:
                if(self.start_date > self.end_date):
                    raise ValidationError("End date must be greater than start date")

    @api.constrains('minimum_purchase','purchase','points','minimum_points')
    def negative_value_check(self):
        if self.minimum_purchase < 0 :
            raise ValidationError("Minimum purchase value must be greater than or equals to zero")

        if self.points < 0 :
            raise ValidationError("Points must be greater than equal to zero")

        if self.purchase < 0 :
            raise ValidationError("Purchase must be greater than equal to zero")

        if self.minimum_points < 0 :
            raise ValidationError("Minimum Points must be greater than equal to zero")

    def write(self, vals):
        if vals.get('config_active'):
            if len(self.search([('config_active', '=', True)])) >= 1:
                raise UserError(_("Sorry, Only one active configuration is allowed."))
        if vals:
            redeem_rule_list_ids = vals.get('redeem_rule_list')
            if redeem_rule_list_ids:
                redeem_list = redeem_rule_list_ids[0][2]
                redeem_rule_objs = self.redeem_rule_list.search([('id','in',redeem_list)])
                for index in range(0,len(redeem_list)-1):
                    for sibling_index in range(index+1,len(redeem_list)):
                        points_ub = redeem_rule_objs[index].points_to
                        points_lb = redeem_rule_objs[index].points_from
                        sibling_ub = redeem_rule_objs[sibling_index].points_to
                        sibling_lb = redeem_rule_objs[sibling_index].points_from
                        if((points_lb >= sibling_lb and points_lb < sibling_ub) or (points_ub > sibling_lb and points_ub <= sibling_ub)) :
                            raise ValidationError("There is some overlapping in Redemption Rule List Range. Please check and assig points range again.")
                        elif((sibling_lb >= points_lb and sibling_lb < points_ub) or (sibling_ub > points_lb and sibling_ub <= points_ub)):
                           raise ValidationError("There is some overlapping in Redemption Rule List Range. Please check and assig points range again.")
        res = super(LoyaltyManagement, self).write(vals)
        if self.config_active:
            for categ in self.env['pos.category'].search([]):
                loyal_categ = self.env['loyalty.category'].search([('category_id','=',categ.id),('loyalty_id','=',self.id)])
                if loyal_categ:
                    categ.write({'wk_point_for_loyalty' : loyal_categ.wk_point_for_loyalty})
                else:
                    categ.write({'wk_point_for_loyalty' : 0})

        return res

    @api.model
    def get_customer_loyality(self, customer_id, total_amount, client_points = 0):
        debit_points = 0
        collapse = False
        loyalty_object = self.search([('config_active', '=', True)])
        if customer_id and client_points>=loyalty_object.minimum_points:
            partner = self.env["res.partner"].browse(customer_id)
            loyality_points = client_points or partner.wk_loyalty_points
            if loyalty_object:
                discount = loyalty_object.with_context(loyality_points=loyality_points).get_discount()
            if discount.get('line_discount'):
                debit_points = float(
                    total_amount if discount.get('total_discount') > total_amount else discount.get('total_discount')) / discount.get('line_discount')
                if debit_points < 0:
                    debit_points = 0
                if loyalty_object.redeem_type=='full':
                    if debit_points<loyality_points:
                        collapse = True
                    debit_points = loyality_points
            return {'discount': discount.get('total_discount'), 'points': partner.wk_loyalty_points, 'customer': customer_id, 'debit_points': debit_points, 'collapse': collapse}
        else:
            return {'discount': 0, 'points': 0, 'customer': 0, 'debit_points': 0, 'collapse': collapse}



    @api.model
    def get_loyalty_product(self):
        loyalty_object = self.search([('config_active', '=', True)])
        if loyalty_object:
            if (loyalty_object.end_date and datetime.now() > datetime.strptime(loyalty_object.end_date, "%Y-%m-%d %H:%M:%S")):
                loyalty_object.write({'config_active':False})
                return False
            return loyalty_object[0].loyality_product_id.id
        return False

    def get_discount(self):
        total_discount, line_discount = 0, 0
        loyality_points = self._context['loyality_points'] if self._context.get('loyality_points') else 0
        for line in self.redeem_rule_list:
            points_to = line.points_to
            points_from = line.points_from
            if (loyality_points >= points_from and loyality_points <= points_to):
                total_discount = loyality_points * line.discount
                line_discount = line.discount
        if not self.redeem_rule_list:
            total_discount = -1
        return {'total_discount': total_discount, 'line_discount': line_discount}


class RedeemRuleList(models.Model):
    _name = 'redeem.rule.list'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            currency = self.env['res.currency'].browse(vals.get('currency_id'))
            vals['name'] = "Rule : " + str(vals.get('points')) + " loyalty points, can be redeem to a discount of " + str(
                vals.get('discount')) + " " + str(currency.name_get()[0][1])
        return super(RedeemRuleList, self).create(vals)

    name = fields.Char(string='Name', size=100, readonly=True, default=lambda self: '/')
    rule_name = fields.Char(string='Rule Name', size=100)
    config_active = fields.Boolean(string='Active', default=True)
    active_rule = fields.Boolean(string="Active Rule", default=True)
    points_from = fields.Integer(string='Loyality Points', required=True)
    points_to = fields.Integer(string='Loyality Points', required=True)
    discount = fields.Float(string='Discount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency of your Company.", default=lambda self: self.env.user.company_id.currency_id.id)

    # @api.one
    @api.constrains('points_from','points_to','discount')
    def point_range_validation(self):
        if(self.points_from < 0 or self.points_to < 0):
            raise ValidationError("Points range must be positve integer type.")
        if(self.discount <= 0):
            raise ValidationError("Discount must be greater than zero.")
        if(self.points_from > self.points_to):
            raise ValidationError("In Redemption Rule List, starting point must be less than ending point")

class PosOrder(models.Model):
    _inherit = "pos.order"

    wk_loyalty_points = fields.Float(string='Loyalty Points', help='The amount of Loyalty points the customer won or lost with this order')

    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        fields['wk_loyalty_points'] = ui_order.get('wk_loyalty_points')
        return fields

    @api.model
    def create_from_ui(self, orders, draft=False):
        data = self.env['res.partner'].search_read([('id','=',18)],['wk_loyalty_points'])
        values = {}
        res = super(PosOrder, self).create_from_ui(orders,draft)
        # ids
        if type(res) == dict:
            ids = res.get('order_ids')
        else:
            ids = res
        for order,order_id in zip(orders,ids or []):
            if order.get('data') and order.get('data').get('wk_loyalty_points') and order.get('data').get('partner_id'):
                partner = self.env['res.partner'].browse(order.get('data').get('partner_id'))
                values.update({'pos_order_id': order_id.get('id'),
                                'session_id': order.get('data').get('pos_session_id'),
                                'customer_id': order.get('data').get('partner_id'),
                                'salesman_id': order.get('data').get('user_id'),
                                'tx_date': order.get('data').get('creation_date').replace('T', ' ')[:19],
                                })
                if order.get('data').get('redeemTaken'):
                    _logger.info("*************{}*********{}******".format(partner.wk_loyalty_points,order.get('data')))
                    remaining_points = abs(partner.wk_loyalty_points - order.get('data').get('debit_points'))
                    values['tx_type'] = 'debit'
                    values['tx_points'] = order.get('data').get('debit_points')
                else:   
                    remaining_points = partner.wk_loyalty_points + order.get('data').get('wk_loyalty_points')
                    values['tx_type'] = 'credit'
                    values['tx_points'] = order.get('data').get('wk_loyalty_points')
                values['remain_points'] = remaining_points
                self.create_loyalty_history(values)
            if order.get('data') and order.get('data').get('wk_loyalty_points') == 0 and order.get('data').get('partner_id'):
                if order.get('data').get('redeemTaken'):
                    partner = self.env['res.partner'].browse(order.get('data').get('partner_id'))
                    values.update({'pos_order_id': order_id.get('id'),
                                   'session_id': order.get('data').get('pos_session_id'),
                                   'customer_id': order.get('data').get('partner_id'),
                                   'salesman_id': order.get('data').get('user_id'),
                                   'tx_date': order.get('data').get('creation_date').replace('T', ' ')[:19],
                                   })
                    remaining_points = order.get('data').get('wk_loyalty_points')
                    values['tx_type'] = 'debit'
                    values['tx_points'] = abs(partner.wk_loyalty_points)
                    values['remain_points'] = remaining_points
                    self.create_loyalty_history(values)
        return ids

    def create_loyalty_history(self, vals):
        try:
            history_obj = self.env['pos.loyalty.history']
            history_obj.create(vals)
        except Exception as e:
            return False
