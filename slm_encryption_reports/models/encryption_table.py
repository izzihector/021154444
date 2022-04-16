from odoo import models, fields, api, _


class EncryptionTable(models.Model):
    _name = "encryption.table"

    year = fields.Integer('Year')
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items',
                               states={'posted': [('readonly', True)]}, copy=True)

    _sql_constraints = [('year_unique', 'unique(year)',
                         'The encryption table for this year already exists')]


class EncryptonTableLine(models.Model):
    _name = "encryption.table.line"

    account_id = fields.Many2one('account.account', string='Account', required=True, index=True,
                                 ondelete="cascade", domain=[('deprecated', '=', False)],
                                 default=lambda self: self._context.get('account_id', False))
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True,
                                          index=True)
    cc_to = fields.Selection([('cc5_cc6', 'CC 5 TO CC6'), ('cc6_cc7', 'CC 6 TO CC 7')], string='', required=True,
                             copy=False, default='cc5_cc6')


