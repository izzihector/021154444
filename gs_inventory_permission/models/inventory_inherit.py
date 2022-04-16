# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockTransferInherit(models.Model):
    _inherit = 'stock.internal.transfer'

    # ###############################  Stock Internal Transfer #########################################################
    is_inv_cancel = fields.Boolean(compute="_get_default_inv_cancel")
    is_inv_draft = fields.Boolean(compute="_get_default_inv_draft")
    is_inv_do_enter = fields.Boolean(compute="_get_default_inv_do_enter")
    is_inv_approved = fields.Boolean(compute="_get_default_inv_approved")
    is_inv_submit = fields.Boolean(compute="_get_default_inv_submit")
    is_inv_print = fields.Boolean(compute="_get_default_inv_print")

    def _get_default_inv_print(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_stock_internal_trans')])
            rec.is_inv_print = False
            if permission:
                if user in permission.inv_print_id.ids:
                    rec.is_inv_print = True

    def _get_default_inv_approved(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_stock_internal_trans')])
            rec.is_inv_approved = False
            if permission:
                if user in permission.inv_approved_id.ids:
                    rec.is_inv_approved = True

    def _get_default_inv_submit(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_stock_internal_trans')])
            rec.is_inv_submit = False
            if permission:
                if user in permission.inv_submit_id.ids:
                    rec.is_inv_submit = True

    def _get_default_inv_cancel(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_stock_internal_trans')])
            rec.is_inv_cancel = False
            if permission:
                if user in permission.inv_cancel_id.ids:
                    rec.is_inv_cancel = True

    def _get_default_inv_draft(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_stock_internal_trans')])
            rec.is_inv_draft = False
            if permission:
                if user in permission.inv_draft_id.ids:
                    rec.is_inv_draft = True

    def _get_default_inv_do_enter(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_stock_internal_trans')])
            rec.is_inv_do_enter = False
            if permission:
                if user in permission.inv_do_enter_id.ids:
                    rec.is_inv_do_enter = True


# ######################################################################################################################
# ###############################  Transfers ###########################################################################

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    is_tr_confirm = fields.Boolean(compute="_get_default_tr_confirm")
    is_tr_assign = fields.Boolean(compute="_get_default_tr_assign")
    is_tr_cancel = fields.Boolean(compute="_get_default_tr_cancel")
    is_tr_validate = fields.Boolean(compute="_get_default_tr_validate")
    is_tr_set_quantities = fields.Boolean(compute="_get_default_tr_set_quantities")
    is_tr_print = fields.Boolean(compute="_get_default_tr_print")
    is_tr_label_layout = fields.Boolean(compute="_get_default_tr_label_layout")
    is_tr_do_unreserve = fields.Boolean(compute="_get_default_tr_do_unreserve")
    is_tr_scrap = fields.Boolean(compute="_get_default_tr_scrap")
    is_tr_toggle_is_locked = fields.Boolean(compute="_get_default_tr_toggle_is_locked")
    is_tr_signature = fields.Boolean(compute="_get_default_tr_signature")
    is_tr_return_picking = fields.Boolean(compute="_get_default_tr_return_picking")

    def _get_default_tr_confirm(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_confirm = False
            if permission:
                if user in permission.tr_confirm_id.ids:
                    rec.is_tr_confirm = True

    def _get_default_tr_assign(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_assign = False
            if permission:
                if user in permission.tr_assign_id.ids:
                    rec.is_tr_assign = True

    def _get_default_tr_cancel(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_cancel = False
            if permission:
                if user in permission.tr_cancel_id.ids:
                    rec.is_tr_cancel = True

    def _get_default_tr_validate(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_validate = False
            if permission:
                if user in permission.tr_validate_id.ids:
                    rec.is_tr_validate = True

    def _get_default_tr_set_quantities(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_set_quantities = False
            if permission:
                if user in permission.tr_set_quantities_id.ids:
                    rec.is_tr_set_quantities = True

    def _get_default_tr_print(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_print = False
            if permission:
                if user in permission.tr_print_id.ids:
                    rec.is_tr_print = True

    def _get_default_tr_label_layout(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_label_layout = False
            if permission:
                if user in permission.tr_label_layout_id.ids:
                    rec.is_tr_label_layout = True

    def _get_default_tr_do_unreserve(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_do_unreserve = False
            if permission:
                if user in permission.tr_do_unreserve_id.ids:
                    rec.is_tr_do_unreserve = True

    def _get_default_tr_scrap(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_scrap = False
            if permission:
                if user in permission.tr_scrap_id.ids:
                    rec.is_tr_scrap = True

    def _get_default_tr_toggle_is_locked(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_toggle_is_locked = False
            if permission:
                if user in permission.tr_toggle_is_locked_id.ids:
                    rec.is_tr_toggle_is_locked = True

    def _get_default_tr_signature(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_signature = False
            if permission:
                if user in permission.tr_signature_id.ids:
                    rec.is_tr_signature = True

    def _get_default_tr_return_picking(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_transfers')])
            rec.is_tr_return_picking = False
            if permission:
                if user in permission.tr_return_picking_id.ids:
                    rec.is_tr_return_picking = True


# ######################################################################################################################
# ###############################  Transfers ###########################################################################

class StockScrapInherit(models.Model):
    _inherit = 'stock.scrap'

    is_so_confirm = fields.Boolean(compute="_get_default_so_confirm")

    def _get_default_so_confirm(self):
        for rec in self:
            user = rec.env.user.id
            permission = self.env['gs.inventory.permission'].search(
                [('permission_type', '=', 'inv_scrap')], limit=1)
            rec.is_so_confirm = False
            if permission:
                if user in permission.so_confirm_id.ids:
                    rec.is_so_confirm = True
