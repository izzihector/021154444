from odoo.exceptions import UserError
from odoo import api, models, fields, exceptions,_


class Reservation_management_wizard(models.TransientModel):
    _name = 'reservation.management.wizard'

    name = fields.Char()