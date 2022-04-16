# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    """ Manufacturing Orders """
    _inherit = "sale.order"

    emi_paid = fields.Integer("invoiced", readonly=True)
    emi_unpaid = fields.Integer("Total EMI", readonly=True)
    is_emi_created = fields.Boolean(string="EMI done?", readonly=True, default=False)
    account_invoice_emi_id = fields.Many2one('account.invoice.emi', string="Account Invoice EMI")

    def action_invoice_emi(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.emi',
            'res_id': self.account_invoice_emi_id.id,
            'views': [[False, "form"]],
        }
        
    def action_create_emi(self):
        if not self.account_invoice_emi_id:
            context = {'default_so_id': self.id,
                       'default_active': True}
            return {
                    'name': _('Account Invoice EMI'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice.emi',
                    'view_id': self.env.ref('account_invoice_emi.view_account_invoice_emi_form').id,
                    'type': 'ir.actions.act_window',
                    'context': context,
                    }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.emi',
            'res_id': self.account_invoice_emi_id.id,
            'views': [[False, "form"]],
        } 
            

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res.is_emi_created = False
        return res


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    
    def _account_invoice_emi_total(self):
        if not self.ids:
            self.total_account_invoice_emi = 0.0
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        account_invoice_emi = self.env['account.invoice.emi'].search([('so_id.partner_id', 'in', all_partner_ids), ('state', '!=', 'draft')])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_account_invoice_emi = len(account_invoice_emi)

    total_account_invoice_emi = fields.Integer(compute='_account_invoice_emi_total', string="Total EMI")
