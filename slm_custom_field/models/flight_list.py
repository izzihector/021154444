# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import fields, models, api


class FlightList(models.Model):
    _name = "flight.list"

    name = fields.Char('VLNR')
    stop1 = fields.Many2one('flight.list.stop', string='TRAJ1', required=False)
    stop2 = fields.Many2one('flight.list.stop', string='TRAJ2', required=False)
    stop3 = fields.Many2one('flight.list.stop', string='TRAJ3', required=False)
    stop4 = fields.Many2one('flight.list.stop', string='TRAJ4', required=False)
    opercde1 = fields.Many2one('profit.center', 'Profit Center')
    retvlnr = fields.Many2one('flight.list', string='RETVLNR')
    charter = fields.Boolean(string='Is charter?')
    cargo = fields.Boolean(string='Is cargo?')
    ferry = fields.Boolean(string='Is ferry?')
    description = fields.Char('Description')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Flight already exists !"),
    ]

    @api.onchange('stop1', 'stop2', 'stop3', 'stop4','charter', 'ferry')
    def _onchange_country_id(self):
        description = ''

        if self.charter:
            if self.stop1 and self.stop2:
                description = 'CHARTER {} TO {}'.format(self.stop1.city, self.stop2.city)
            elif self.stop1:
                description = 'CHARTERS FROM {}'.format(self.stop1.city)
            elif self.stop2:
                description = 'CHARTERS TO {}'.format(self.stop2.city)

        elif self.ferry:
            description = 'FERRY'
        else:
            description = "{} - {}".format(self.stop1.city, self.stop2.city)
            if self.stop3:
                description += " - {}".format(self.stop3.city)
            if self.stop4:
                description += " - {}".format(self.stop4.city)

        self.description = description

    def name_get(self):
        result = []
        for record in self:
            name = '{}  '.format(record.name )
            if record.stop1:
                name += '{} - '.format(record.stop1.name)
            else:
                name += '- '
            if record.stop2:
                name += '{}'.format(record.stop2.name)

            if record.stop3:
                name += ' - {}'.format(record.stop3.name)
            if record.stop4:
                name += ' - {}'.format(record.stop4.name)

            result.append((record.id, name))
        return result


class FlightListStop(models.Model):
    _name = "flight.list.stop"

    name = fields.Char('IATA code')
    city = fields.Char('City')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "This stop already exists !"),
        ('city_uniq', 'unique (city)', "This stop already exists !")
    ]
