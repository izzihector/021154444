# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import models, fields


class Stock_Move(models.Model):
    _inherit = 'stock.move'

    def _action_done(self):
        res = super(Stock_Move, self)._action_done()
        for each_move in res:
            if each_move.inventory_id and each_move.inventory_id.is_backdated_inv:
                each_move.write(
                    {'date': each_move.inventory_id.inv_backdated or fields.Datetime.now(),
                     'date_expected': each_move.inventory_id.inv_backdated or fields.Datetime.now(),
                     'note': each_move.inventory_id.backdated_remark, 'origin': each_move.inventory_id.backdated_remark})
                each_move.move_line_ids.write(
                    {'date': each_move.inventory_id.inv_backdated or fields.Datetime.now()})
        return res
