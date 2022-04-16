from odoo import api, models ,fields,_
from odoo.exceptions import AccessError, ValidationError


class RoomCapacity(models.Model):
    _name='hotel.room.capacity'

    name = fields.Char()
    date_day = fields.Date()
    hotel_id = fields.Many2one('hotel.management', )
    room_type_id = fields.Many2one('hotel.room.type', domain="[('hotel_id','=',hotel_id)]")

    total_rooms = fields.Integer(related='room_type_id.total_rooms',store=True,)
    available_room = fields.Integer(compute="calc_available_rooms",store=True,string='Remaining', readonly=True)
    reserved_room = fields.Integer(readonly=True)

    @api.depends('total_rooms','reserved_room')
    def calc_available_rooms(self):
        for rec in self:
            print("+====================+")
            rec.available_room = rec.total_rooms - rec.reserved_room
        return True

    # @api.multi
    @api.constrains('reserved_room')
    def reservation_rooms_constrain(self):
        for rec in self:
            if rec.reserved_room > rec.total_rooms :
                raise ValidationError(_("You can't Reserve For thos day " + fields.Date.to_string(rec.date_day)))