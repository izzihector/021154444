from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class RoomCostAttribute(models.Model):
    _name = 'room.cost.attribute'
    _inherit = ['portal.mixin',  'mail.thread', 'mail.activity.mixin']
    _rec_name = 'room_type_id'

    name = fields.Char()
    hotel_id = fields.Many2one('hotel.management', required=True, tracking=True)
    room_type_id = fields.Many2one('hotel.room.type', required=True, tracking=True,
                                   domain="[('hotel_id','=',hotel_id)]")
    ordered_by = fields.Many2one('res.partner', string='Partner', tracking=True)
    rate_supplier = fields.Many2one('res.partner', required=True, tracking=True)
    date_from = fields.Date(required=True, tracking=True)
    period_lead_id = fields.Many2one('date.range', string='Period', )
    date_to = fields.Date(required=True, tracking=True)
    note = fields.Char(tracking=True)
    price_ids = fields.One2many('cost.per.person', 'room_type_id', required=True, tracking=True)
    children_price_ids = fields.One2many('cost.per.children', 'room_type_id', required=True, tracking=True)
    # remove this only for db
    cost = fields.Integer(tracking=True)

    meal_plan = fields.Selection([
        ('Soft Al Inclusive', 'Soft Al Inclusive'),
        ('Half Board (HB)', 'Half Board (HB)'),
        ('Full Board (FB)', 'Full Board (FB)'),

    ], required=True, tracking=True)

    # ('Al Inclusive', 'Al Inclusive'),
    # ('Board (B)', 'Board (B)'),
    @api.constrains('date_to', 'date_from')
    def condition_on_date(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from > rec.date_to:
                    raise ValidationError(_('date from must be less than date to'))

    @api.constrains('date_to', 'date_from', 'rate_supplier', 'meal_plan', 'hotel_id', 'room_type_id')
    def condition_on_date_all_conditions(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                all_room_cost = self.env['room.cost.attribute'].search(
                    [('id', '!=', rec.id), ('hotel_id', '=', rec.hotel_id.id),
                     ('room_type_id', '=', rec.room_type_id.id),
                     ('rate_supplier', '=', rec.rate_supplier.id),
                     ('meal_plan', '=', rec.meal_plan),
                     '|', '&', ('date_from', '>=', rec.date_from), ('date_to', '<=', rec.date_to),
                     '|', '&', ('date_from', '<=', rec.date_from), ('date_to', '>=', rec.date_from),
                     '&', ('date_from', '<=', rec.date_to), ('date_to', '>=', rec.date_to), ])
                if all_room_cost:
                    raise ValidationError(
                        "Dates overlapped, please make sure dates are correct " + str(all_room_cost.id))
                if len(rec.price_ids) <= 0:
                    raise ValidationError('Please one add price Lines')

    @api.onchange('period_lead_id')
    def get_period_lead_dates(self):
        for rec in self:
            rec.date_from = rec.period_lead_id.date_start
            rec.date_to = rec.period_lead_id.date_end


class CostPerPerson(models.Model):
    _name = 'cost.per.person'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    person_per_room = fields.Selection([
        ('1', 'Single'), ('2', 'Double'),
        ('3', 'Triple'), ('4', '4 Persons'),
        ('5', '5 Persons')], required=True, string="Occupancy", default='1', tracking=True)
    hotel_cost = fields.Monetary("Room Cost", required=True, currency_field='currency_id', tracking=True)
    hotel_profit = fields.Monetary('Profit', compute='calc_profit_from_hotel', currency_field='currency_id', store=True,
                                   )
    guest_price = fields.Monetary("Selling Price", required=True, currency_field='currency_id', tracking=True)
    room_type_id = fields.Many2one('room.cost.attribute')
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.constrains('hotel_cost', 'guest_price')
    def money_constrains(self):
        for rec in self:
            if rec.hotel_cost == 0 or rec.guest_price == 0:
                raise ValidationError('Hotel Cost and Guest price Must Be greater than zero')

    @api.depends('guest_price', 'hotel_cost')
    def calc_profit_from_hotel(self):
        for rec in self:
            if rec.hotel_cost and rec.guest_price:
                rec.hotel_profit = rec.guest_price - rec.hotel_cost


class CostPerChildren(models.Model):
    _name = 'cost.per.children'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    # person_per_room = fields.Selection([
    #     ('1', 'Single'), ('2', 'Double'),
    #     ('3', 'Triple'), ('4', '4 Persons'),
    #     ('5', '5 Persons')], required=True, string="Occupancy", default='1', tracking=True)
    child_sequence = fields.Selection([('first_child', 'First Child Below'), ('second_child', 'Second Child Below'),
                                       ('third_child', 'Third Child Below')],required=True, tracking=True)
    age = fields.Float(required=True, tracking=True)
    hotel_cost = fields.Monetary("Room Cost", required=True, currency_field='currency_id', tracking=True)
    hotel_profit = fields.Monetary('Profit', compute='calc_profit_from_hotel', currency_field='currency_id', store=True,
                                   )
    guest_price = fields.Monetary("Selling Price", required=True, currency_field='currency_id', tracking=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    room_type_id = fields.Many2one('room.cost.attribute')

    @api.constrains('hotel_cost', 'guest_price')
    def money_constrains(self):
        for rec in self:
            if rec.hotel_cost == 0 or rec.guest_price == 0:
                raise ValidationError('Hotel Cost and Guest price Must Be greater than zero')

    @api.depends('guest_price', 'hotel_cost')
    def calc_profit_from_hotel(self):
        for rec in self:
            if rec.hotel_cost and rec.guest_price:
                rec.hotel_profit = rec.guest_price - rec.hotel_cost
