# -*- coding: utf-8 -*-
# Part of Softhealer Technologies

from odoo import api, fields, models
from datetime import date


class MrpProductionn(models.Model):
    _inherit = 'mrp.production'

    remarks = fields.Text(string="Remarks")
    is_remarks = fields.Boolean(
        related="company_id.remark_for_mrp_production", string="Is Remarks")
    is_remarks_mandatory = fields.Boolean(
        related="company_id.remark_mandatory_for_mrp_production", string="Is remarks mandatory")
    is_boolean = fields.Boolean()

    @api.onchange('date_planned_start')
    def onchange_date_planned_start(self):
        if str(self.date_planned_start.date()) < str(date.today()):
           self.is_boolean = True
        else:
            self.is_boolean = False
