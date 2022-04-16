# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class ResCurrency(models.Model):
	_inherit = 'res.currency'

	currency_code = fields.Char(string="Currency Code", required=False)

