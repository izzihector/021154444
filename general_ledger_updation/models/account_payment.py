# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.invoice':
            return rec

        invoices = self.env['account.invoice'].browse(active_ids)
        #pnr_airway = ','.join([inv.pnr_airway for inv in invoices if inv.pnr_airway])
        #rec.update({
        #    'pnr_airway': pnr_airway or '',
        #})
        return rec
