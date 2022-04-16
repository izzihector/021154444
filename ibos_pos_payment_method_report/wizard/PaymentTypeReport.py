# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosDetails(models.TransientModel):
    _name = 'pos.sales.report.wizard'
    _description = 'Point of Sale Details Report'

    from_date = fields.Date(string="From Date", default=fields.Datetime.now)
    to_date = fields.Date(string="To Date", default=fields.Datetime.now)
    payment_method_id = fields.Many2many('pos.payment.method', 'name', string='Payment Method', required=True)

    def get_pay_details(self):
        data = {
            'payment_method_id': self.payment_method_id.ids,
            'from_date': self.from_date,
            'to_date': self.to_date,
        }
        return self.env.ref('ibos_pos_payment_method_report.action_report_by_payment_type_customer').report_action(self, data=data)


