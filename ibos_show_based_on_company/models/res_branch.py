from odoo import fields, models, api

class ResBranch(models.Model):
    _inherit = 'res.branch'

    company_id = fields.Many2one('res.company')