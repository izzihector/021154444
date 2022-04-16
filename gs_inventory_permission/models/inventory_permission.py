# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GsInventoryPermission(models.Model):
    _name = 'gs.inventory.permission'
    _description = 'Inventory Permission'
    # _rec_name = 'permission_type'

    permission_type = fields.Selection([
                                        ('inv_stock_internal_trans', 'Stock Internal Transfer'),
                                        ('inv_transfers', 'Transfers'),
                                        ('inv_scrap', 'Scrap Orders'),
                                         ], required=1, string="Permission Type")

    # Stock Internal Transfer
    inv_cancel_id = fields.Many2many("res.users", "user_id_st06", "user_id_st006", "user_id_st0006", string="Cancel")
    inv_draft_id = fields.Many2many("res.users", "user_id_st07", "user_id_st007", "user_id_st0007", string="Reset to Draft")
    inv_do_enter_id = fields.Many2many("res.users", "user_id_st08", "user_id_st008", "user_id_st0008", string="Send & Receive")
    inv_approved_id = fields.Many2many("res.users", "user_id_st09", "user_id_st009", "user_id_st0009", string="Approved")
    inv_submit_id = fields.Many2many("res.users", "user_id_st010", "user_id_st0010", "user_id_st00010", string="Submit")
    inv_print_id = fields.Many2many("res.users", "user_id_st011", "user_id_st0011", "user_id_st00011", string="Print")

    # Transfers
    tr_confirm_id = fields.Many2many("res.users", "user_id_tr01", "user_id_tr001", "user_id_tr0001", string="Confirm")
    tr_assign_id = fields.Many2many("res.users", "user_id_tr02", "user_id_tr002", "user_id_tr0002", string="Check Availability")
    tr_cancel_id = fields.Many2many("res.users", "user_id_tr03", "user_id_tr003", "user_id_tr0003", string="Cancel")
    tr_validate_id = fields.Many2many("res.users", "user_id_tr04", "user_id_tr004", "user_id_tr0004", string="Validate")
    tr_set_quantities_id = fields.Many2many("res.users", "user_id_tr05", "user_id_tr005", "user_id_tr0005", string="Set quantities")
    tr_print_id = fields.Many2many("res.users", "user_id_tr06", "user_id_tr006", "user_id_tr0006", string="Print")
    tr_label_layout_id = fields.Many2many("res.users", "user_id_tr07", "user_id_tr007", "user_id_tr0007", string="Print Labels")
    tr_do_unreserve_id = fields.Many2many("res.users", "user_id_tr08", "user_id_tr008", "user_id_tr0008", string="Unreserve")
    tr_scrap_id = fields.Many2many("res.users", "user_id_tr09", "user_id_tr009", "user_id_tr0009", string="Scrap")
    tr_toggle_is_locked_id = fields.Many2many("res.users", "user_id_tr010", "user_id_tr0010", "user_id_tr00010", string="Unlock & lock")
    tr_signature_id = fields.Many2many("res.users", "user_id_tr011", "user_id_tr0011", "user_id_tr00011", string="Sign")
    tr_return_picking_id = fields.Many2many("res.users", "user_id_tr012", "user_id_tr0012", "user_id_tr00012", string="Return")

    # Scrap Orders
    so_confirm_id = fields.Many2many("res.users", "user_id_so01", "user_id_so001", "user_id_so0001", string="Confirm")
