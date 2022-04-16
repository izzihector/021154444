# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from uuid import uuid4

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CashConfig(models.Model):
    _name = 'cash.config'
    _order = 'id desc'
    _description = 'Cash Config'

    def _default_sale_journal(self):
        return self._default_invoice_journal()

    def _default_invoice_journal(self):
        return self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

    name = fields.Char(string='Config Name', required=True, readonly=True, default='/')
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=False)
    journal_ids = fields.Many2many('account.journal', 'cash_config_journal_rel','cash_config_id', 'journal_id', string='Available Payment Methods', domain="[('journal_user', '=', True ), ('type', 'in', ['bank', 'cash'])]",)
    cash_control = fields.Boolean(string='Cash Control', help="Check the amount of the cashbox at opening and closing.")
    session_ids = fields.One2many('cash.session', 'config_id', string='Sessions')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    journal_id = fields.Many2one('account.journal', string='Sales Journal', domain=[('type', '=', 'sale')], help="Accounting journal used to post sales entries.", default=_default_sale_journal)
    user_id = fields.Many2one('res.users', string="User")

    _sql_constraints = [('uniq_name', 'unique(name)',
                         "The name of this Cash Session must be unique !")]

    @api.depends('journal_id.currency_id', 'journal_id.company_id.currency_id')
    def _compute_currency(self):
        for cash_config in self:
            if cash_config.journal_id:
                cash_config.currency_id = cash_config.journal_id.currency_id.id or cash_config.journal_id.company_id.currency_id.id
            else:
                cash_config.currency_id = self.env.user.company_id.currency_id.id

    @api.model
    def create(self, values):
        config_name = self.env['ir.sequence'].next_by_code('cash.config')
        if values.get('name'):
            config_name += ' ' + values['name']
        values.update({
            'name': config_name,
        })
        return super(CashConfig, self).create(values)
