# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class PosConfigExtended(models.Model):
    _inherit = 'pos.config'

    is_multi_uom_shown = fields.Boolean(string='Change Product UOM', help='Show a button to change the UOM of selected orderline.')
