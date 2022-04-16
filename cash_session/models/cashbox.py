# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class CashboxLine(models.Model):
	_inherit = 'account.cashbox.line'
	
	currency_id = fields.Many2one('res.currency', string="Currency", required=True, readonly=False)
	journal_id = fields.Many2one('account.journal', 'Journal', required=True, readonly=False)
	cash_session_id = fields.Many2one('cash.session', related="cashbox_id.cash_session_id", string="Session", copy=False)

	@api.onchange('journal_id', 'currency_id')
	def onchange_journal(self):
		if self.journal_id:
			self.currency_id = self.journal_id.currency_id

CashboxLine()

class AccountBankStmtCashWizard(models.Model):
	_inherit = 'account.bank.statement.cashbox'

	cash_session_id = fields.Many2one('cash.session', string="Session", copy=False)



AccountBankStmtCashWizard()