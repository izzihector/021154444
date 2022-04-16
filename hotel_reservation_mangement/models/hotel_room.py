from odoo import api, fields, models
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class HotelRoom(models.Model):
    _name = 'hotel.room.view'

    name = fields.Char()


class HotelRoomType(models.Model):
    _name = 'hotel.room.type'

    name = fields.Char()
    hotel_id = fields.Many2one('hotel.management')
    view_type = fields.Many2one('hotel.room.view')
    total_rooms = fields.Integer(required=True, string="Contracted")

    # @api.multi
    # @api.depends('name', 'hotel_id')
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         name = self.name
    #         if self.hotel_id:
    #             name = "[" + self.hotel_id.name + '] ' + name
    #         res += [(record.id, name)]
    #     return res

    note = fields.Text()
    bedding_type = fields.Selection([
        ('Single', 'Single'),
        ('Twin (2 single)', 'Twin (2 single)'),
        ('Twin (2 double)', 'Twin (2 double)'),
        ('Double', 'Double'),
        ('Triple', 'Triple'),
        ('King Bed', 'King Bed'),
        ('Queen Bed', 'Queen Bed'),

    ])
    room_aperture = fields.Selection([
        ('Balcony', 'Balcony'),
        ('Balcony/Terrace', 'Balcony/Terrace'),
        ('French Balcony', 'French Balcony'),
        ('Run of the House', 'Run of the House'),
        ('Terrace', 'Terrace'),
        ('Window', 'Window'),
    ])

    facilities_ids = fields.Many2many('hotel.room.facilities')

    maximum_adults = fields.Integer()
    minimum_adults = fields.Integer()
    maximum_children = fields.Integer()
    minimum_children = fields.Integer()
    maximum_persons = fields.Integer()


class HotelRoomFacilities(models.Model):
    _name = 'hotel.room.facilities'

    name = fields.Char()
