from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch', string="Business Unit")
    responsible_ids = fields.Many2many('res.users', string="Responsible Person", domain="[('branch_id', '=', branch_id)]")
