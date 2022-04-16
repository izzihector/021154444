# -*- encoding: UTF-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AirfareDetails(models.Model):
    _name = "airfare.details"

    name = fields.Char(string="Route Name")
    date = fields.Date("Date", required=True)
    total_seats = fields.Integer("Total Seats", required=True)
    total_pax = fields.Integer('Total Pax')
    total_blockhours = fields.Float('Total Block hours')
    total_kilograms = fields.Float('Total Kilograms')
    total_flights = fields.Integer('Total Single Flights')
    vlnr = fields.Many2one('flight.list', string='VLNR')
