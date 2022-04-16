# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import re


class Payment(models.Model):
	_inherit = 'account.payment'
	
	@api.onchange('journal_ids', 'session_id', 'payment_type', 'currency_id', 'amount')
	def onchange_journals(self):
		res = {}
		journal_ids = []
		if self.session_id:
			for journal in self.journal_ids:
				journal_ids.append(journal.id)
		#res = {}
		if journal_ids:
			if self.payment_type == 'transfer':
				res['domain'] = {'journal_id': [('id', 'in', journal_ids)], 'destination_journal_id': [('id', 'in', journal_ids)]}
			else:
				res['domain'] = {'journal_id': [('id', 'in', journal_ids)]}
		return res
	
		

	@api.model
	def default_get(self, fields):
		rec = super(Payment, self).default_get(fields)
		active_ids = self._context.get('active_ids')
		invoices = self.env['account.move'].browse(active_ids)
		rec.update({
			'journal_id': False,
			'invoice_number': ' '.join([ref for ref in invoices.mapped('name') if ref]),
		})
		return rec
Payment()

