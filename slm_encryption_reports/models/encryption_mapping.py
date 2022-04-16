# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class EncryptionMapping(models.Model):
    _name = 'encryption.mapping'
    fiscal_year = fields.Many2one('account.fiscal.year', 'Fiscal Year')
    date_from = fields.Date('Date from', related="fiscal_year.date_from")
    date_to = fields.Date('Date to', related="fiscal_year.date_to")
    line_ids = fields.One2many('encryption.mapping.line', 'encryption_mapping_id', string='Encryption lines', copy=True)


class EncryptionMappingLine(models.Model):
    _name = 'encryption.mapping.line'

    encryption_mapping_id = fields.Many2one('encryption.mapping', string='Encryption Mapping', ondelete="cascade",
                                            index=True, required=True, auto_join=True)
    analytical_account_id = fields.Many2one('account.analytic.account', 'Analytical Account')
    cost_center = fields.Many2one('account.analytic.account', 'Cost Center')
    encryption = fields.Float('Encryption', digits=(12, 3))
