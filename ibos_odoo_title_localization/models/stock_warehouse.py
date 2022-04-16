# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools


class Outlate(models.Model):
    _inherit = "stock.warehouse"

    def _default_name(self):
        count = self.env['stock.warehouse'].with_context(active_test=False).search_count(
            [('company_id', '=', self.env.company.id)])
        return "%s - Outlet # %s" % (self.env.company.name, count + 1) if count else self.env.company.name

    name = fields.Char('Outlet', index=True, required=True, default=_default_name)

    # warehouse_view_location
    view_location_id = fields.Many2one('stock.location', string='Outlets view location')
