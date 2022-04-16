# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class ResBranch(models.Model):
	_inherit = 'res.branch'

	branch_code = fields.Char(string="Branch Code", required=False)

