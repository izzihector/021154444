# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProcessFlow(models.Model):
    _name = 'process.flow'

    name = fields.Char(string="Process Flow", required=True)
