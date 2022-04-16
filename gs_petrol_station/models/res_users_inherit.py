# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    station_ids = fields.Many2many("gs.petrol.station", "station_ids01", "station_ids001",
                                        "station_ids0001", string="Station")