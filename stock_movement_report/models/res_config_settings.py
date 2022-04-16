# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    inv_movement_rec_limit = fields.Integer(string="Records Limit", default=80,
            help="Limit the number of records to display on screen at a time.", config_parameter='stock_movement_report.inv_movement_rec_limit')
