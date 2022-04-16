# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class GSDailySales(models.Model):
    _name = 'gs.sales.register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sales Register'
    _rec_name = "station_id"

    sales_register_ids = fields.One2many('gs.sales.register.line', 'link_id')
    station_id = fields.Many2one('gs.petrol.station', string='Station')
    date = fields.Date(string='Date', default=fields.Date.context_today)

    @api.onchange('station_id')
    def domain_station_id(self):
        return {'domain': {'station_id': [('id', 'in', self.env.user.station_ids.ids)]}}


class GSDailySalesLine(models.Model):
    _name = 'gs.sales.register.line'

    link_id = fields.Many2one('gs.sales.register')
    station_id = fields.Many2one('gs.petrol.station', string='Station')
    date = fields.Date(string='Date', default=fields.Date.context_today )
    type_pump_id = fields.Many2one('gs.pump.type', string='Pump Type')
    pump_id = fields.Many2one('gs.pump', string='Pump')
    nozzle_petrol_id = fields.Many2one('gs.nozzle.petrol', string='Nozzle Petrol')
    product_id = fields.Many2one('product.product', string='Product', related='type_pump_id.product_id',)
    opening_pump = fields.Float(string='Opening',)
    ending_pump = fields.Float(string='Ending',)
    sales = fields.Float(string='Sales',)
    user_id = fields.Many2one('res.users', string='User')

    @api.onchange('date')
    def _onchange_date(self):
        for rec in self:
            rec.station_id = rec.link_id.station_id
        if self.station_id:
            list = []
            pump = self.env['gs.pump'].search([('station_id', '=', self.station_id.id)])
            for pu in pump:
                list.append(pu.id)
            domain = {'pump_id': [('id', 'in', list)]}
            return {'domain': domain}

