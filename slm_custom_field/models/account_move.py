# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Luis Aquino -- Xetechs, S.A.
#    Copyright (C) 2019-Today Xetechs (<https://www.xetechs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api
from .mandatory_analytic_account import MandatoryAnalyticAccount


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    vestcd = fields.Integer('VESTCD')
    dagb = fields.Integer('DAGB')
    stuknr = fields.Char('STUKNR')
    regnr = fields.Char('REGNR')
    boekjr = fields.Integer('BOEKJR')
    per = fields.Integer('PER')
    dag = fields.Integer('DAG')
    mnd = fields.Integer('MND')
    jaar = fields.Integer('JAAR')
    faktnr = fields.Char('FAKTNR')
    pnr = fields.Char('PNR')
    omschr = fields.Char('OMSCHR')
    controlle = fields.Char('CONTROLLE')
    curcd = fields.Integer('CURCD')
    bedrag = fields.Float('BEDRAG')
    bedrsrd = fields.Float('BEDRSRD')
    bedrusd = fields.Float('BEDRUSD')
    opercde = fields.Integer('OPERCDE')
    vlnr = fields.Many2one('flight.list', 'VLNR')
    # vlnr = fields.Char('VLNR')
    gallon = fields.Float('GALLON')
    plcde = fields.Char('PLCDE')
    handl = fields.Char('HANDL', default="0")
    maalt = fields.Char('MAALT', default="0")
    pax = fields.Integer('PAX')
    mandgn = fields.Integer('MANDGN')
    sdatum = fields.Integer('SDATUM')
    kstnpl6 = fields.Many2one('account.analytic.account', string='KSTNPL6')
    kstnpl7 = fields.Many2one('account.analytic.account', string='KSTNPL7')
    persnr = fields.Integer('SEATS')
    ponr = fields.Integer('CARGO KG')
    galprijs = fields.Float('GALPRIJS')
    betrekdg = fields.Integer('BETREKDG')
    betrekmd = fields.Integer('BETREKMD')
    betrekjr = fields.Integer('BETREKJR')
    factdg = fields.Integer('FACTDG')
    factmd = fields.Integer('FACTMD')
    factjr = fields.Integer('FACTJR')
    vltype = fields.Char('VLTYPE')
    vltreg = fields.Char('VLTREG')
    required_flight_number = fields.Boolean('Is the fligh number required? (internal field)',
                                            compute='_is_flight_number_required')
    required_analytic_account = fields.Boolean(
        'Is the analytical account required? (internal field)', default=False)

    @api.onchange('account_id')
    def _filter_analytic_account(self):
        for record in self:
            if record.account_id:
                code = record.account_id.code
                if (code[0] in ['4', '8', '9']) and code != '999999':
                    record.required_analytic_account = True
                else:
                    record.required_analytic_account = False
                analytic_accounts = MandatoryAnalyticAccount.search_mandatory_accounts(
                    code, self.env.cr)
                record.analytic_account_id = None
                if analytic_accounts:
                    res = {
                        'domain': {'analytic_account_id': [('id', 'in', analytic_accounts)]}
                    }
                else:
                    res = {
                        'domain': {'analytic_account_id': []}
                    }
                return res

    @api.depends('analytic_account_id', 'account_id')
    def _is_flight_number_required(self):
        for record in self:
            record.required_flight_number = False
            if record.account_id and record.analytic_account_id:
                if MandatoryAnalyticAccount.check_required_fligh_number(record.account_id.code, record.analytic_account_id.id,
                                                                        self.env.cr):
                    record.required_flight_number = True


AccountMoveLine()
