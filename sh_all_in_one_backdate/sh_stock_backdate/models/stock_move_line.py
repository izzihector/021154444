# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

from operator import mod
from odoo import fields, models,api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    date = fields.Datetime(related = "move_id.date",default=fields.Datetime.now,)

    remarks_for_picking = fields.Text(string = "Remarks for picking",related="move_id.remarks_for_picking")
    is_remarks_for_picking = fields.Boolean(related="company_id.remark_for_picking",string = "Is Remarks for picking")

    remarks_for_scrap = fields.Text(string = "Remarks for scrap",related="move_id.remarks_for_scrap")
    is_remarks_for_scrap = fields.Boolean(related="company_id.remark_for_scrap",string = "Is Remarks for scrap")

    