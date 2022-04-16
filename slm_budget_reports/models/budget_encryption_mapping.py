# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date


class BudgetEncryptionMapping(models.Model):
    _name = 'budget.encryption.mapping'

    months = [("{:02d}".format(m), date(datetime.today().year, m, 1).strftime('%B').capitalize()) for m in range(1, 13)]
    years = [(str(y), str(y)) for y in range(2019, 2050)]

    year = fields.Selection(years, string='Year', default=lambda y: datetime.today().strftime('%Y'))
    month = fields.Selection(months, string='Month')
    line_ids = fields.One2many('budget.encryption.mapping.line', 'budget_encryption_mapping_id',
                               string='Budget Encryption lines', copy=True)

    _order = "year desc,month desc"

    def name_get(self):
        return [(record.id, "{} {}".format(record.year, dict(self.months).get(record.month))) for record in self]

    
    @api.onchange('month', 'year')
    def _onchange_month(self):
        budget_mapping = self.env['budget.encryption.mapping'].search([('year', '=', self.year),
                                                                       ('month', '=', self.month)])
        if budget_mapping:
            self.month = None
            warning = {
                'title': _('Warning!'),
                'message': _('The budget for this month already exists')}

            return {'warning': warning}

    
    def duplicate_data(self):
        sql = """
            SELECT analytical_account_id, cost_center, encryption
                FROM budget_encryption_mapping_line
                WHERE budget_encryption_mapping_id = (SELECT BEM.id
                                                        FROM budget_encryption_mapping BEM
                                                        JOIN budget_encryption_mapping_line BEML
                                                                 ON (BEM.id = BEML.budget_encryption_mapping_id)
                                                        WHERE BEM.id != %s
                                                        ORDER BY year DESC ,month DESC LIMIT 1)
                ORDER BY id
        """

        self.env.cr.execute(sql, (self.id,))
        results = self.env.cr.dictfetchall()
        line_ids = [(0, 0, {'analytical_account_id': x['analytical_account_id'], 'cost_center': x['cost_center'],
                            'encryption': x['encryption']}) for x in results]
        self.line_ids.unlink()
        self.update({'line_ids': line_ids})


class BudgetEncryptionMappingLine(models.Model):
    _name = 'budget.encryption.mapping.line'

    budget_encryption_mapping_id = fields.Many2one('budget.encryption.mapping', string='Budget Encryption Mapping',
                                                   ondelete="cascade", index=True, required=True, auto_join=True)
    analytical_account_id = fields.Many2one('account.analytic.account', 'Analytical Account')
    cost_center = fields.Many2one('account.analytic.account', 'Cost Center')
    encryption = fields.Float('Encryption', digits=(12, 3))
