from odoo import fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    branch_id = fields.Many2one('res.branch', string='Business Unit', related='session_id.config_id.branch_id', required=True)
