from odoo import api,fields,models


class ReservationInvoice(models.Model):
    _inherit = 'account.move'

    hotel_id = fields.Many2one('hotel.management', )
    room_type = fields.Many2one('hotel.room.type', domain="[('hotel_id','=',hotel_id)]")
    meal_plan = fields.Selection([
        ('Soft Al Inclusive', 'Soft Al Inclusive'),
        ('Half Board (HB)', 'Half Board (HB)'),
        ('Full Board (FB)', 'Full Board (FB)'),

    ], required=True, tracking=True)
    arrival_date = fields.Date(string="Check In")
    nights_quantity = fields.Integer(string="Nights #")
    departure_date = fields.Date(string="Check Out")
    reservation_id = fields.Many2one('hotel.reservation.management', string="Reservation", readonly=True)