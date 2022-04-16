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
from odoo import api, fields, models


class Accountmove(models.Model):
    _inherit = "account.move"

    # # Aca metemos el nuevo diccionario que contiene las columnas agregadas en la factura y que ya existen
    # #   En el Asiento Contable por el modulo slm_custom_fields
    @api.model
    def invoice_line_move_line_get(self):
        res = super(Accountmove, self).invoice_line_move_line_get()
        for inv_line in self.invoice_line_ids:
            for line in res:
                if inv_line.id == line['invl_id']:
                    line.update({
                        'opercde': str(inv_line.opercde),
                        'vlnr': inv_line.vlnr and inv_line.vlnr.id or False,
                        'gallon': str(inv_line.gallon),
                        'plcde': str(inv_line.plcde),
                        'handl': str(inv_line.handl),
                        'maalt': str(inv_line.maalt),
                        'pax': str(inv_line.pax),
                        'mandgn': str(inv_line.mandgn),
                        'galprijs': str(inv_line.galprijs),
                        'factdg': str(inv_line.factdg),
                        'factmd': str(inv_line.factmd),
                        'factjr': str(inv_line.factjr),
                        'vltype': str(inv_line.vltype),
                        'vltreg': str(inv_line.vltreg),
                    })
        return res

    def action_move_create(self):
        res = super(Accountmove, self).action_move_create()
        for inv_line in self.invoice_line_ids:
            for line in self.move_id.line_ids:
                if (bool(inv_line.product_id) and (inv_line.product_id.id == line.product_id.id)) or \
                        ((inv_line.price_total == line.credit) & (inv_line.account_id == line.account_id) and
                         (inv_line.account_analytic_id == line.analytic_account_id) and
                         (inv_line.name == line.name)):
                    line.write({
                        'opercde': inv_line.opercde,
                        'vlnr': inv_line.vlnr and inv_line.vlnr.id or False,
                        'gallon': inv_line.gallon,
                        'plcde': inv_line.plcde,
                        'handl': inv_line.handl,
                        'maalt': inv_line.maalt,
                        'pax': inv_line.pax,
                        'mandgn': inv_line.mandgn,
                        'galprijs': inv_line.galprijs,
                        'factdg': inv_line.factdg,
                        'factmd': inv_line.factmd,
                        'factjr': inv_line.factjr,
                        'vltype': inv_line.vltype,
                        'vltreg': inv_line.vltreg,
                    })
        return res


Accountmove()


class AccountmoveLine(models.Model):
    _inherit = "account.move.line"

    opercde = fields.Char('OPERCDE')
    vlnr = fields.Many2one('flight.list', 'VLNR')
    gallon = fields.Char('GALLON', default="0.00")
    plcde = fields.Char('PLCDE')
    handl = fields.Char('HANDL', default="0")
    maalt = fields.Char('MAALT', default="0")
    pax = fields.Char('PAX', default="0")
    mandgn = fields.Char('MANDGN', default="0")
    galprijs = fields.Char('GALPRIJS', default="0.00")
    factdg = fields.Char('FACTDG')
    factmd = fields.Char('FACTMD')
    factjr = fields.Char('FACTJR')
    vltype = fields.Char('VLTYPE')
    vltreg = fields.Char('VLTREG')


AccountmoveLine()
