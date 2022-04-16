from odoo import fields,models,api


class ReservationCancelation(models.Model):
    _name = 'reservation.cancelation'


    reservation_id = fields.Many2one('hotel.reservation.management')
