# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class AccountJournal(models.Model):
	_inherit = 'account.journal'

	day_book = fields.Char(string="Day Book", required=False)
