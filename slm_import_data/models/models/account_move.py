# -*- coding: utf-8 -*-

import time
from datetime import date
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree


class AccountMove(models.Model):
	_inherit = "account.move"
	
	
	def create_move_margo(self):
		cr = self.env.cr
		move_obj = self.env['account.move']
		move_line_obj = self.env['account.move.line']
		#try:
		sql = ('''select se.id as id , se.branch_code as branch_code, se.day_book as day_book, se.piece_number as piece_number,\
						se.registration_number as registration_number, se.book_year as book_year, se.period as period, se.account_number as account_number,\
						se.cost_center as cost_center, se.invoice_number as invoice_number, se.description as description, se.currency_code as currency_code,\
						se.amount as amount, se.amount_srd as amount_srd, se.amount_usd as amount_usd, se.operation_code, se.date as date, se.date_read as date_read,\
						se.ticketnumber as ticketnumber, se.row_count as row_count, se.flag1 as flag1\
						from slm_edgar_sales se\
						where se.flag1 = false and se.sheet_name = 'SALES';''')
		cr.execute(sql,[])
		for row in cr.dictfetchall():
			#line = self.create_invoice_line_edgar(row)
			inv = {
				'partner_id': 424,
				'number': row['invoice_number'],
				'move_name': row['invoice_number'],
				'date_invoice': datetime.strptime(str(row['date']),'%Y-%m-%d %H:%M:%S').date(),
				'journal_id': self.get_journal(row['day_book']) or False,
				'branch_id': self.get_branch(row['branch_code']) or False,
				'company_id': self.get_company(row['branch_code']) or False,
				'account_id': self.get_account(row['account_number'], row['branch_code']) or False,
				'piece_number': int(row['piece_number']),
				'reference': row['ticketnumber'],
				'book_year': row['book_year'],
				'period': row['period'],
				'type': 'out_invoice',
				'state': 'draft',
				'invoice_line_ids': [(0, 0, line)],
			}
			invoice_id = invoice_obj.create(inv)
		#except Exception as e:
		#print(e)
		#pass
		
	
	def get_analytic_account(self, account_number, branch_code, analytic_account):
		account_obj = self.env['account.account']
		analytic_account_obj = self.env['account.analytic.tag']
		account_id = False
		company_id = False
		if account_number:
			if branch_code:
				company_id = self.get_company(branch_code)
			account_id = account_obj.search([('code', '=', account_number), ('company_id', '=', company_id)], limit=1)
		return account_id.id
	
	
	def get_branch(self, branch_code):
		branch_obj = self.env['res.branch']
		#res = False
		branch_id = False
		if branch_code:
			branch_id = branch_obj.search([('branch_code', '=', branch_code)], limit=1)
		return branch_id.id
	
	
	def get_account(self, account_number, branch_code):
		account_obj = self.env['account.account']
		account_id = False
		company_id = False
		if account_number:
			if branch_code:
				company_id = self.get_company(branch_code)
			account_id = account_obj.search([('code', '=', account_number), ('company_id', '=', company_id)], limit=1)
		return account_id.id

	
	def get_company(self, branch_code):
		branch_obj = self.env['res.branch']
		#res = False
		branch_id = False
		if branch_code:
			branch_id = branch_obj.search([('branch_code', '=', branch_code)], limit=1)
		return branch_id.company_id.id
	
	
	def get_journal(self, day_book):
		journal_obj = self.env['account.journal']
		journal_id = False
		if day_book:
			journal_id = journal_obj.search([('day_book', '=', day_book)], limit=1)
		return journal_id.id
AccountMove()

