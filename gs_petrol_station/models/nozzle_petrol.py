# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class GSNozzlePetrol(models.Model):
    _name = 'gs.nozzle.petrol'
    _description = 'Pump Type'

    name = fields.Char(string='Name', )