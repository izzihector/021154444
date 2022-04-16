# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _


class AccountMove(models.Model):
    _inherit = "account.move"