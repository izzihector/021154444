from odoo import fields, models,tools, api, _
from datetime import date, time, datetime
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import psycopg2


class resPartner(models.Model):
	_inherit = 'res.partner'

	@api.model_create_multi
	def create(self, vals):
		res = super(resPartner, self).create(vals)
		print('res[id]', res['id'])
		partnerCredit = {'partner_id': res['id'], 'credit_jr': 0.0, 'update': 0.0}
		partnerCrd = self.env["partner.credit"].sudo().create(partnerCredit)
		return res