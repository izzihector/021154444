# -*- coding: utf-8 -*-
import json
import time
import logging
from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)


# class SgeedeUomUomInherit(models.Model):
#     _inherit = "uom.uom"
#
#     def _compute_quantity(self, qty, to_unit, round=False, rounding_method='UP', raise_if_failure=True):
#         """ Convert the given quantity from the current UoM `self` into a given one
#             :param qty: the quantity to convert
#             :param to_unit: the destination UoM record (uom.uom)
#             :param raise_if_failure: only if the conversion is not possible
#                 - if true, raise an exception if the conversion is not possible (different UoM category),
#                 - otherwise, return the initial quantity
#         """
#         if not self or not qty:
#             return qty
#         self.ensure_one()
#
#         if self != to_unit and self.category_id.id != to_unit.category_id.id:
#             if raise_if_failure:
#                 raise UserError(_('The unit of measure %s defined on the order line doesn\'t belong to the same category as the unit of measure %s defined on the product. Please correct the unit of measure defined on the order line or on the product, they should belong to the same category.') % (self.name, to_unit.name))
#             else:
#                 return qty
#
#         if self == to_unit:
#             amount = qty
#         else:
#             amount = qty / self.factor
#             if to_unit:
#                 amount = amount * to_unit.factor
#
#         if to_unit and round:
#             amount = tools.float_round(amount, precision_rounding=to_unit.rounding, rounding_method=rounding_method)
#
#         return amount


class stock_internal_transfer(models.Model):
    _name = 'stock.internal.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Stock Internal Transfer'

    def print_stock_internal_transfer_report(self):
        return self.env.ref('sgeede_internal_transfer.stock_internal_transfer_action').report_action(self)

    def make_activity_user(self, user):
        date_deadline = fields.Date.today()
        note = _("Please Review This Stock Internal Transfer")
        summary = _("Stock Internal Transfer")

        self.sudo().activity_schedule(
            'mail.mail_activity_data_todo', date_deadline,
            note=note,
            user_id=user.id,
            res_id=self.id,
            summary=summary
        )

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_submit(self):
        for rec in self:
            users = self.env['gs.inventory.permission'].search([('permission_type', '=', 'inv_stock_internal_trans')])
            for user in users.inv_approved_id:
                rec.make_activity_user(user)
            rec.write({'state': 'submit'})
        return True

    def action_approved(self):
        for rec in self:
            users = self.env['gs.inventory.permission'].search([('permission_type', '=', 'inv_stock_internal_trans')])
            for user in users.inv_do_enter_id:
                rec.make_activity_user(user)
            rec.write({'state': 'approved'})
        return True

    def action_send(self):
        self.write({'state': 'send'})
        return True

    def action_receive(self):
        self.write({'state': 'done'})
        return True

    def do_enter_wizard(self):
        ctx = dict(self._context)

        ctx.update({
            'active_model': self._name,
            'active_ids': self._ids,
            'active_id': len(self._ids) and self._ids[0] or False
            })

        created_id = self.env['wizard.stock.internal.transfer'].with_context(ctx).create({'transfer_id': len(self._ids) and self._ids or False}).id
        return self.env['wizard.stock.internal.transfer'].with_context(ctx).wizard_view(created_id)

    name = fields.Char(string= 'Reference', track_visibility="onchange", default= lambda self: self.env['ir.sequence'].next_by_code('stock.internal.transfer') or '')
    date = fields.Datetime(string= 'Date', track_visibility="onchange", default= lambda self: time.strftime('%Y-%m-%d %H:%M:%S'))
    source_warehouse_id = fields.Many2one('stock.warehouse', string="Source Warehouse", track_visibility="onchange")
    dest_warehouse_id = fields.Many2one('stock.warehouse', string="Destination Warehouse", track_visibility="onchange")
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('approved', 'Approved'), ('send', 'Send'), ('done', 'Done'),('cancel', 'Cancel'), ], string="Status", track_visibility="onchange", default="draft")
    line_ids = fields.One2many('stock.internal.transfer.line', 'transfer_id', string="Stock Internal Transfer Line")
    picking_ids = fields.One2many('stock.picking', 'transfer_id', string="Picking")
    backorder_id = fields.Many2one('stock.internal.transfer', 'Backorder')


class stock_internal_transfer_line(models.Model):
    _name = 'stock.internal.transfer.line'
    _inherit = 'mail.thread'

    @api.onchange('product_id')
    def product_id_change(self):
        result = {}
        if not self.product_id: {
            'product_uom_id': False,
        }
        product = self.env['product.product'].browse(self.product_id.id)
        #if product.second_uom_id:
        #    product_uom_id = product.second_uom_id and product.second_uom_id.id or False
        #else:    
        #    product_uom_id = product.uom_id and product.uom_id.id or False
        product_uom_id = product.uom_id and product.uom_id.id or False
        result['value'] = {'product_uom_id': product_uom_id}
        return result

    name = fields.Char(string="Reference", track_visibility='onchange')
    product_id = fields.Many2one('product.product', string="Product", track_visibility="onchange")
    qty_available = fields.Float('On Hand', related='product_id.qty_available')
    product_qty = fields.Float(string="Quantity", track_visibility="onchange",)
    product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure", track_visibility='onchange')
    state = fields.Selection([('cancel', 'Cancel'), ('draft', 'Draft'), ('send', 'Send'), ('done', 'Done')],
        string="Status", track_visibility='onchange', default="draft")
    transfer_id = fields.Many2one('stock.internal.transfer', string="Transfer", track_visibility="onchange")
    # sh_sec_uom = fields.Many2one(
    #     "uom.uom",
    #     'Secondary UOM',
    #     compute="_compute_secondary_uom",
    #     readonly=False
    # )
    # sh_sec_qty = fields.Float(
    #     "Secondary Qty",
    #     digits='Product Unit of Measure',
    #     compute="_compute_product_uom_qty_sh",
    #     readonly=False
    # )
    #
    # sh_is_secondary_unit = fields.Boolean(
    #     "Related Sec Unit",
    #
    # )
    # related="product_id.sh_is_secondary_unit"

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        if self.product_qty:
            if self.qty_available < self.product_qty:
                raise ValidationError(_("Quantity Bigger Than Quantity On Hand."))

    # @api.onchange('product_id')
    # def _onchange_product_id_is_secondary_unit(self):
    #     for rec in self:
    #         if rec.product_id.sh_is_secondary_unit:
    #             rec.sh_is_secondary_unit = True
    #         else:
    #             rec.sh_is_secondary_unit = False

    # @api.depends('product_qty', 'product_uom_id')
    # def _compute_product_uom_qty_sh(self):
    #     if self:
    #         for rec in self:
    #             if rec.sh_is_secondary_unit and rec.sh_sec_uom:
    #                 rec.sh_sec_qty = rec.product_uom_id._compute_quantity(
    #                     rec.product_qty,
    #                     rec.sh_sec_uom,
    #                 )
    #             else:
    #                 rec.sh_sec_qty = 0.0
    #
    #             float_num = rec.sh_sec_qty - int(rec.sh_sec_qty)
    #             int_num = int(rec.sh_sec_qty)
    #             if float_num > 0.25:
    #                 int_num += 1
    #                 rec.sh_sec_qty = int_num
    #             else:
    #                 rec.sh_sec_qty = int(rec.sh_sec_qty)

    # @api.depends('product_id', 'product_uom_id')
    # def _compute_secondary_uom(self):
    #     if self:
    #         for rec in self:
    #             if rec.product_id and rec.product_id.sh_is_secondary_unit and rec.product_id.uom_id:
    #                 rec.sh_sec_uom = rec.product_id.sh_secondary_uom.id
    #             elif not rec.product_id.sh_is_secondary_unit:
    #                 rec.sh_sec_uom = False
    #                 rec.sh_sec_qty = 0.0

    # @api.onchange('sh_sec_qty', 'sh_sec_uom')
    # def onchange_sh_sec_qty_sh(self):
    #     if self and self.sh_is_secondary_unit and self.sh_sec_uom:
    #         self.product_qty = self.sh_sec_uom._compute_quantity(
    #             self.sh_sec_qty, self.product_uom_id
    #         )
