# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,tools, api, _
from datetime import date, time, datetime
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import psycopg2


class PosConfig(models.Model):
	_inherit = 'pos.config'
	
	invoice_credit_payment = fields.Selection([('full_amount', 'Full Amount(without credit)'), ('partial_amount', 'Partial Amount(with credit)')],string='',default='full_amount')


class AccountJournal(models.Model):
	_inherit = 'account.journal'

	credit_jr = fields.Boolean(string='POS Credit Journal')   


class PosPaymentMethod(models.Model):
	_inherit = 'pos.payment.method'

	credit_jr = fields.Boolean(string='POS Credit Journal',related='journal_id.credit_jr',readonly=False)  


class PosOrder(models.Model):
	_inherit = 'pos.order'
	
	credit_check = fields.Boolean('Credit')

	def action_pos_order_credit_invoice(self,cr_journal):
		moves = self.env['account.move']

		for order in self:
			# Force company for all SUPERUSER_ID action
			if order.account_move:
					moves += order.account_move
					continue

			if not order.partner_id:
				raise UserError(_('Please provide a partner for the sale.'))

			move_vals = order._prepare_invoice_vals()
			new_move = order._create_invoice(move_vals)

			crd_amt = 0
			for pymt in order.payment_ids : 
				if pymt.payment_method_id.credit_jr:
					crd_amt += pymt.amount

			if crd_amt != 0 :
				new_move.update({'invoice_line_ids': [(0, 0, {
						'move_id': new_move.id,
						'quantity': 1,
						'name': 'Credit',
						'price_unit': - float(crd_amt),
						'account_id': self.env['account.account'].search([('internal_type','=', 'other')], limit=1).id, 				
					})]
				})

			order.write({'account_move': new_move.id, 'state': 'invoiced'})
			moves += new_move

		if not moves:
			return {}

		return {
			'name': _('Customer Invoice'),
			'view_mode': 'form',
			'view_id': self.env.ref('account.view_move_form').id,
			'res_model': 'account.move',
			'context': "{'move_type':'out_invoice'}",
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': moves and moves.ids[0] or False,
		}
		

	@api.model
	def _process_order(self, order, draft, existing_order):
		"""Create or update an pos.order from a given dictionary.

		:param pos_order: dictionary representing the order.
		:type pos_order: dict.
		:param draft: Indicate that the pos_order is not validated yet.
		:type draft: bool.
		:param existing_order: order to be updated or False.
		:type existing_order: pos.order.
		:returns number pos_order id
		"""
		to_invoice = order['to_invoice'] if not draft else False
		order = order['data']
		pos_session = self.env['pos.session'].browse(order['pos_session_id'])
		if pos_session.state == 'closing_control' or pos_session.state == 'closed':
			order['pos_session_id'] = self._get_valid_session(order).id

		pos_order = False
		if not existing_order:
			pos_order = self.create(self._order_fields(order))
		else:
			pos_order = existing_order
			pos_order.lines.unlink()
			order['user_id'] = pos_order.user_id.id
			pos_order.write(self._order_fields(order))

		self._process_payment_lines(order, pos_order, pos_session, draft)

		add_credit_in_invoice = False
			
		for pos_credit in pos_order.payment_ids:
			if pos_credit.payment_method_id.credit_jr == True:
				vals = {
					'pos_order_id': pos_order.id,
					'partner_id': pos_order.partner_id.id,
					'used_credit_amount' :pos_credit.amount,
					'date' : pos_order.date_order,
					'pos_order_amount' : pos_order.amount_total,
					'balance_credit_amount' : pos_order.partner_id.custom_credit,
				}
				self.env['credit.history'].sudo().create(vals)	


		if not draft:
			try:
				pos_order.action_pos_order_paid()
			except psycopg2.DatabaseError:
				# do not hide transactional errors, the order(s) won't be saved!
				raise
			except Exception as e:
				_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

		if to_invoice:
			cr_journal = 0.0
			st = order
			ps = self.env['pos.session'].search([('id','=',st['pos_session_id'])])
			add_credit_in_invoice = ps.config_id.invoice_credit_payment
			for st1 in st['statement_ids']:
				pymnt_jrnl= self.env['pos.payment.method'].browse(int(st1[2]['payment_method_id']))
				if pymnt_jrnl.credit_jr:
					cr_journal = (st1[2]['amount'])
			if cr_journal and add_credit_in_invoice == 'partial_amount':

				pos_order.action_pos_order_credit_invoice(cr_journal)
				pos_order.account_move.sudo().with_context(force_company=self.env.user.company_id.id).post()

			else:
				pos_order.action_pos_order_invoice()
				pos_order.account_move.sudo().with_context(force_company=self.env.user.company_id.id)
		return pos_order.id	
