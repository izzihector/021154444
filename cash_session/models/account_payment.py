# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import re


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _default_session(self):
        return self.env['cash.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)

    session_id = fields.Many2one('cash.session', string='Session', required=False, index=True, domain="[('state', '=', 'opened')]", states={'draft': [('readonly', False)]}, readonly=True, default=_default_session)
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True, copy=False)
    statement_ids = fields.One2many('account.bank.statement.line', 'cash_statement_id', string='Payments', states={'draft': [('readonly', False)]}, readonly=True)
    invoice_number = fields.Char(string='Invoice Number', readonly=True, states={'draft': [('readonly', False)]})
    journal_ids = fields.Many2many('account.journal', related='session_id.journal_ids', readonly=True, string='Available Payment Methods')

    def _write(self, values):
        if 'invoice_number' in values:
            inv = values["invoice_number"]
            if inv:
                inv = re.sub('\ |\?|\.|\!|\/|\;|\:|\-|\,', '', inv)
                inv = inv.upper()
                values["invoice_number"] = inv
        res = super(AccountPayment, self)._write(values)
        return res

    @api.model
    def create(self, values):
        if 'invoice_number' in values:
            inv = values["invoice_number"]
            if inv:
                inv = re.sub('\ |\?|\.|\!|\/|\;|\:|\-|\,', '', inv)
                inv = inv.upper()
                values["invoice_number"] = inv
        res = super(AccountPayment, self).create(values)
        return res
