from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
import datetime
from datetime import date,timedelta


class CustomerOrderDetails(models.TransientModel):
    _name = 'pos.customer.details.wizard'
    _description = 'Point of Sale customer order Details Report'

    start_date = fields.Datetime(required=True, default=fields.Datetime.now())
    end_date = fields.Datetime(required=True, default=fields.Datetime.now())
    type = fields.Selection([('all', 'All'), ('summary', 'Summary')], default='all', string='Type')
    order_by = fields.Selection([('date', 'Date'), ('due', 'Due'), ('paid', 'paid'), ('total', 'Total')],
                                default='date', string='Type')
    pos_customer_ids = fields.Many2many('res.partner', string="customers", required= True)
    pos_config = fields.Many2many('pos.config', default=lambda s: s.env['pos.config'].search([]))

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    def generate_report(self):
        # print("self is", self)
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'type': self.type,
                'customer_ids': self.pos_customer_ids.ids, 'pos_config_ids': self.pos_config.ids}
        # print("data is", data)
        return self.env.ref('ibos_customer_order_history.pos_customer_order_details').report_action([], data=data)