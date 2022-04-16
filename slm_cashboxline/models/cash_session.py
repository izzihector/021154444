from odoo import fields, models, api, _


class Session(models.Model):
        _inherit = 'cash.session'

        total = fields.Float(compute='_compute_total', string='Total', digits=0, readonly=True)

        @api.depends('cashbox_lines_ids')
        def _compute_total(self):
                """ Calculates Total"""
                total = 0
                for line in self.cashbox_lines_ids:
                        total += line.subtotal
                self.total = total