from odoo import api, models , fields,_
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError


class SplitRoom(models.Model):
    _name = 'split.room'
    _inherit = ['mail.thread']

    room_name = fields.Char(required=True ,  string="Room Number")
    name = fields.Char(required=True ,  string="Guest Name")
    room_quantity = fields.Integer(default=1, readonly=True)
    person_per_room = fields.Selection([
        ('1','Single'),('2','Double'),
        ('3','Triple'),('4','4 Persons'),
        ('5','5 Persons')] , string="Occupancy",default='2')
    children = fields.Integer()
    hotel_id = fields.Many2one('hotel.management', )
    room_type = fields.Many2one('hotel.room.type', domain="[('hotel_id','=',hotel_id)]")
    meal_plan = fields.Selection([
        ('Soft Al Inclusive', 'Soft Al Inclusive'),
        ('Half Board (HB)', 'Half Board (HB)'),
        ('Full Board (FB)', 'Full Board (FB)'),

    ], required=True, tracking=True)

    reservation_id = fields.Many2one('hotel.reservation.management')
    arrival_date = fields.Date(track_visibility='onchange', string="Check in")
    departure_date = fields.Date(track_visibility='onchange', string="Check Out")
    nights_quantity = fields.Integer(string="Nights", compute='_set_departure_date',store=True)
    nights_price = fields.Integer(string="Total Price", compute='_calc_average_price', store=True,)
    avr_price = fields.Integer("Avr Selling Price" ,readonly=False)

    @api.depends('avr_price')
    def _calc_average_price(self):
        for rec in self:
            # print(rec.nights_price,"in AVR")
            rec.update({'nights_price': rec.avr_price * rec.nights_quantity})

    @api.onchange('children','person_per_room')
    def max_min_constrains(self):
        maximum_adults = self.room_type.maximum_adults
        minimum_adults = self.room_type.minimum_adults
        maximum_children = self.room_type.maximum_children
        minimum_children = self.room_type.minimum_children
        maximum_persons = self.room_type.maximum_persons
        if int(self.person_per_room) > maximum_adults:
            raise ValidationError(_("Adults are greater than Maximum ."))
        elif int(self.person_per_room) < minimum_adults:
            raise ValidationError(_("Adults are less than Minimum ."))
        if int(self.children) > maximum_children:
            raise ValidationError(_("Children are greater than Maximum ."))
        elif int(self.children) < minimum_children:
            raise ValidationError(_("Children are less than Minimum ."))
        if (int(self.children) + int(self.person_per_room) ) > maximum_persons:
            raise ValidationError(_("Total Adults and Children are Grater than Maximum Persons."))

    # odoo 11
    # @api.depends('departure_date')
    # def _set_departure_date(self):
    #     for date in self:
    #         print("i am in night onchange")
    #         if date.arrival_date:
    #             arrival_date = datetime.strptime(date.arrival_date, DATE_FORMAT)
    #             departure_date = datetime.strptime(date.departure_date, DATE_FORMAT)
    #             departure_date = departure_date - arrival_date
    #             nights_q = departure_date.days
    #             date.update({'nights_quantity':nights_q})
    #             print(nights_q , "DDDDDD")

    @api.depends('departure_date')
    def _set_departure_date(self):
        for date in self:
            if date.arrival_date == False or date.departure_date == False:
                raise ValidationError('Please Add Departure Date and Arrival Date First')
            if date.arrival_date:
                arrival_date = date.arrival_date
                departure_date = date.departure_date
                # print(departure_date)
                # print(departure_date - arrival_date)
                nights_q = (departure_date - arrival_date).days
                date.update({'nights_quantity': nights_q})

    @api.onchange('room_type', 'person_per_room', 'meal_plan','nights_quantity', 'room_quantity')
    def calc_room_price_for_total_guests(self):
        # print("i am in cal function")
        for rec in self:
            arrival_price = 0
            departure_price = 0
            nights_price = 0
            if rec.room_type and rec.person_per_room and rec.meal_plan and rec.room_type:
                room_cost_ids = rec.env['room.cost.attribute'].search([
                    ('hotel_id', '=', rec.hotel_id.id),
                    ('room_type_id', '=', rec.room_type.id),
                    ('meal_plan', '=', rec.meal_plan),
                ])

                for room_cost_id in room_cost_ids:
                    # print(room_cost_ids,room_cost_ids)
                    # print(rec.arrival_date,room_cost_id.date_from)
                    if rec.arrival_date >= room_cost_id.date_from and rec.departure_date <= room_cost_id.date_to:
                        # print(rec.arrival_date, "arrival_date",rec.departure_date,'departure_date')
                        for price_id in room_cost_id.price_ids:
                            # print(price_id.guest_price, "Price Guest")
                            if rec.person_per_room == price_id.person_per_room:
                                # print(price_id.guest_price,"Price Guest ############")
                                nights_price = price_id.guest_price * rec.nights_quantity
                                # rec.update({'nights_price':price_id.guest_price})
                                # print(rec.nights_quantity,"=====")
                    elif rec.arrival_date >= room_cost_id.date_from and rec.arrival_date <= room_cost_id.date_to:
                        # print(rec.arrival_date,"arr",room_cost_id.date_from,room_cost_id.date_to)
                        nights = room_cost_id.date_to - rec.arrival_date + relativedelta(days=1)
                        # print(nights.days,"Nights Nights")
                        for price_id in room_cost_id.price_ids:
                            # print(price_id.guest_price, "Price Guest")
                            if rec.person_per_room == price_id.person_per_room:
                                # print(price_id.guest_price,"Price Guest arrive ############")
                                arrival_price = price_id.guest_price * nights.days
                                # print(arrival_price,"arrival_price ")
                                # rec.update({'nights_price':price_id.guest_price})
                    elif rec.departure_date >= room_cost_id.date_from  and rec.departure_date <= room_cost_id.date_to:
                        # print(rec.departure_date,"arr",room_cost_id.date_from,room_cost_id.date_to)
                        nights = rec.departure_date - room_cost_id.date_from
                        for price_id in room_cost_id.price_ids:
                            # print(price_id.guest_price, "Price Guest depar")
                            if rec.person_per_room == price_id.person_per_room:
                                # print(price_id.guest_price,nights.days,"Price Guest depart ############")
                                departure_price = price_id.guest_price * nights.days
                                # print(departure_price,"departure Price")
            nights_price += (departure_price + arrival_price)
            rec.update({'nights_price': nights_price, 'avr_price': nights_price/rec.nights_quantity})

    # @api.multi
    def cancel_reservation_calendar(self):
        room_cal_obj = self.env['hotel.room.capacity']
        for reservation_nights in range(0, self.nights_quantity):
            # print(reservation_nights,"Night#")
            day_date = self.arrival_date + timedelta(days=reservation_nights)
            # print(day_date)
            room_cal_id = room_cal_obj.search(
                [('hotel_id', '=', self.hotel_id.id), ('room_type_id', '=', self.room_type.id),
                 ('date_day', '=', day_date)])
            if room_cal_id:
                # print(room_cal_id, "==========================")
                reserved_room = room_cal_id.reserved_room - 1
                room_cal_id.reserved_room = reserved_room

    # @api.multi
    def reservation_calendar(self):
        room_cal_obj = self.env['hotel.room.capacity']
        for reservation_nights in range(0, self.nights_quantity):
            day_date = self.arrival_date + timedelta(days=reservation_nights)
            # print(day_date)
            room_cal_id = room_cal_obj.search(
                [('hotel_id', '=', self.hotel_id.id), ('room_type_id', '=', self.room_type.id),
                 ('date_day', '=', day_date)])
            # print(room_cal_id, "==========================")
            if room_cal_id:
                reserved_room = self.room_quantity + room_cal_id.reserved_room
                if reserved_room > room_cal_id.total_rooms:
                    raise ValidationError(_("You are Exceed Reservations Rooms For that day " + fields.Date.to_string(
                        room_cal_id.date_day)))
                room_cal_id.reserved_room = reserved_room
            else:
                room_cal_obj.create(
                    {'date_day': day_date, 'room_type_id': self.room_type.id, 'hotel_id': self.hotel_id.id,
                     'reserved_room': self.room_quantity})
        return True


class res_partner(models.Model):
    _inherit = 'res.partner'

    # @api.multi
    def send_mail_template(self):
        # Find the e-mail template
        template = self.env.ref('hotel_reservation_mangement.example_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)