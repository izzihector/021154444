from odoo import api, models, fields, _
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError


class SplitRoom(models.Model):
    _name = 'children.split.room'
    _inherit = ['portal.mixin',  'mail.thread', 'mail.activity.mixin']

    room_name = fields.Char(required=True, string="Room Number")
    name = fields.Char(required=True, string="Guest Name", tracking=True)
    room_quantity = fields.Integer(default=1, readonly=True, tracking=True)
    person_per_room = fields.Selection([
        ('1', 'Single'), ('2', 'Double'),
        ('3', 'Triple'), ('4', '4 Persons'),
        ('5', '5 Persons')], string="Occupancy", default='2', tracking=True)

    hotel_id = fields.Many2one('hotel.management', )
    room_type = fields.Many2one('hotel.room.type', domain="[('hotel_id','=',hotel_id)]", tracking=True)
    meal_plan = fields.Selection([
        ('Soft Al Inclusive', 'Soft Al Inclusive'),
        ('Half Board (HB)', 'Half Board (HB)'),
        ('Full Board (FB)', 'Full Board (FB)'),

    ], required=True, tracking=True)
    child_sequence = fields.Selection([('first_child', 'First Child Below'),
                                       ('second_child', 'Second Child Below'),
                                       ('third_child', 'Third Child Below')], required=True, tracking=True)
    reservation_id = fields.Many2one('hotel.reservation.management')
    arrival_date = fields.Date(tracking=True, string="Check in")
    departure_date = fields.Date(tracking=True, string="Check Out")
    nights_quantity = fields.Integer(string="Nights", compute='_set_departure_date', store=True, tracking=True)
    nights_price = fields.Integer(string="Total Price", compute='_calc_average_price', store=True, tracking=True)
    avr_price = fields.Integer("Avr Selling Price", readonly=False, tracking=True)

    @api.depends('avr_price')
    def _calc_average_price(self):
        for rec in self:
            print(rec.nights_price, "in AVR")
            rec.update({'nights_price': rec.avr_price * rec.nights_quantity})

    @api.depends('departure_date')
    def _set_departure_date(self):
        for date in self:
            if date.arrival_date == False or date.departure_date == False:
                raise ValidationError('Please Add Departure Date and Arrival Date First')
            if date.arrival_date:
                arrival_date = date.arrival_date
                departure_date = date.departure_date
                print(departure_date)
                print(departure_date - arrival_date)
                nights_q = (departure_date - arrival_date).days
                date.update({'nights_quantity': nights_q})

    @api.onchange('room_type', 'child_sequence', 'meal_plan', 'nights_quantity', 'room_quantity')
    def calc_room_price_for_total_guests(self):
        print("i am in cal function")
        for rec in self:
            arrival_price = 0
            departure_price = 0
            nights_price = 0
            print(rec.hotel_id , rec.child_sequence ,rec.meal_plan , rec.room_type)
            if rec.hotel_id and rec.child_sequence and rec.meal_plan and rec.room_type:
                room_cost_ids = rec.env['room.cost.attribute'].search([
                    ('hotel_id', '=', rec.hotel_id.id),
                    ('room_type_id', '=', rec.room_type.id),
                    ('meal_plan', '=', rec.meal_plan),
                ])
                print(room_cost_ids)
                for room_cost_id in room_cost_ids:
                    print(room_cost_ids, room_cost_ids)
                    print(rec.arrival_date, room_cost_id.date_from)
                    if rec.arrival_date >= room_cost_id.date_from and rec.departure_date <= room_cost_id.date_to:
                        print(rec.arrival_date, "arrival_date", rec.departure_date, 'departure_date')
                        for price_id in room_cost_id.children_price_ids:
                            print(price_id.guest_price, "Price Guest")
                            if rec.child_sequence == price_id.child_sequence:
                                print(price_id.guest_price, "Price Guest ############")
                                nights_price = price_id.guest_price * rec.nights_quantity
                                # rec.update({'nights_price':price_id.guest_price})
                                print(rec.nights_quantity, "=====")
                    elif rec.arrival_date >= room_cost_id.date_from and rec.arrival_date <= room_cost_id.date_to:
                        print(rec.arrival_date, "arr", room_cost_id.date_from, room_cost_id.date_to)
                        nights = room_cost_id.date_to - rec.arrival_date + relativedelta(days=1)
                        print(nights.days, "Nights Nights")
                        for price_id in room_cost_id.children_price_ids:
                            print(price_id.guest_price, "Price Guest")
                            if rec.child_sequence == price_id.child_sequence:
                                print(price_id.guest_price, "Price Guest arrive ############")
                                arrival_price = price_id.guest_price * nights.days
                                print(arrival_price, "arrival_price ")
                                # rec.update({'nights_price':price_id.guest_price})
                    elif rec.departure_date >= room_cost_id.date_from and rec.departure_date <= room_cost_id.date_to:
                        print(rec.departure_date, "arr", room_cost_id.date_from, room_cost_id.date_to)
                        nights = rec.departure_date - room_cost_id.date_from
                        for price_id in room_cost_id.children_price_ids:
                            print(price_id.guest_price, "Price Guest depar")
                            if rec.child_sequence == price_id.child_sequence:
                                print(price_id.guest_price, nights.days, "Price Guest depart ############")
                                departure_price = price_id.guest_price * nights.days
                                print(departure_price, "departure Price")
            nights_price += (departure_price + arrival_price)
            rec.update({'nights_price': nights_price, 'avr_price': nights_price / rec.nights_quantity})
