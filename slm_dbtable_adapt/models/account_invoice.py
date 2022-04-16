# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    piece_number = fields.Integer(string="Piece Number", required=False, )
    book_year = fields.Char(string="Book Year", required=False, )
    period = fields.Char(string="Period", required=False, )

