# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    branch_id = fields.Many2one('res.branch')

    def _select(self):
        return super(PosOrderReport, self)._select() + ", ps.branch_id as branch_id"

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ", ps.branch_id"