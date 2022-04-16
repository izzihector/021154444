# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class GSPetrolStation(models.Model):
    _name = 'gs.petrol.station'
    _description = 'Petrol Station'

    code = fields.Char(string='Code', )
    name = fields.Char(string='Name', )
    partner_id = fields.Many2one('res.partner', 'Customer')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    petrol_station_ids = fields.One2many('gs.petrol.station.line', 'link_id')


class GSPetrolStationLine(models.Model):
    _name = 'gs.petrol.station.line'

    link_id = fields.Many2one('gs.petrol.station')
    pump = fields.Char(string='Pump')
    type_pump_id = fields.Many2one('gs.pump.type', string='Pump Type')
    nozzle_petrol_id = fields.Many2one('gs.nozzle.petrol', string='Nozzle Petrol')

