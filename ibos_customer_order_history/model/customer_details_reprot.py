import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64
from datetime import datetime

_logger = logging.getLogger(__name__)


class CustomerReport(models.AbstractModel):
    _name = "report.ibos_customer_order_history.customer_order_details"
    _description = 'Customer Order details'

    def get_credit_details(self, date_start=False, date_stop=False, customer_ids=False,
                           configs=False, type=False, ession_ids=False):

        date_start_format = fields.Datetime.from_string(date_start).date()
        date_end_format = fields.Datetime.from_string(date_stop).date()

        if date_start:
            date_start = fields.Datetime.from_string(date_start).replace(hour=0, minute=0, second=0)
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))
        if date_stop:
            date_stop = fields.Datetime.from_string(date_stop).replace(hour=23, minute=59, second=59)
            # avoid a date_stop smaller than date_start
            if (date_stop < date_start):
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)


        customer_history = []

        for customer in customer_ids:
            pos_order_ids = self.env['pos.order'].search(['&', '&', ('partner_id', '=', customer.id),
                                                          ('date_order', '>=', fields.Datetime.to_string(date_start)),
                                                          ('date_order', '<=', fields.Datetime.to_string(date_stop))],
                                                         order="date_order desc")
            customer_name = customer.name
            data = []
            paid = 0.0
            due = 0.0
            total = 0.0
            test = {}

            for order in pos_order_ids:
                if order.partner_id.id == customer.id:
                    paid += abs(order.amount_paid)
                    for payment in order.payment_ids:
                        due += (payment.amount if payment.payment_method_id.name == "Credit" or payment.payment_method_id.name == "credit" else 0.00)
                        current_due = (payment.amount if payment.payment_method_id.name == "Credit" or payment.payment_method_id.name == "credit" else 0.00)
                    total += order.amount_total
                    if type == 'all':
                        data.append({
                            'date': fields.Datetime.from_string(order.date_order).date(),
                            'receipt_no': order.name,
                            'order_ref': order.pos_reference,
                            'paid': round(order.amount_paid),
                            'due': round(current_due),
                            'total':    round(order.amount_total)
                        })
                    if type == 'summary':
                        if len(test) == 0:
                            test[fields.Datetime.from_string(order.date_order).date()] = {
                                'date': fields.Datetime.from_string(order.date_order).date(),
                                'paid': round(order.amount_paid),
                                'due': round(current_due),
                                'total': round(order.amount_total)
                            }
                        else:
                            # if fields.Datetime.from_string(order.date_order).date() in test.keys():
                            if fields.Datetime.from_string(order.date_order).date() in test.keys():
                                test[fields.Datetime.from_string(order.date_order).date()]['paid'] += round(order.amount_paid)
                                test[fields.Datetime.from_string(order.date_order).date()]['due'] += round(current_due)
                                test[fields.Datetime.from_string(order.date_order).date()]['total'] += round(order.amount_total)
                            else:
                                test[fields.Datetime.from_string(order.date_order).date()] = {
                                    'date': fields.Datetime.from_string(order.date_order).date(),
                                    'paid': round(order.amount_paid),
                                    'due': round(current_due),
                                    'total': round(order.amount_total)
                                }
            if type == 'summary':
                data = [dict for key, dict in test.items()]

            customer_history.append({
                'name': customer_name,
                'date_from': date_start_format,
                'date_to': date_end_format,
                'data': data,
                'total_paid': round(paid),
                'total_due': round(due),
                'total_total': round(total),
                'street': customer.street,
                'street2': customer.street2,
                'city': customer.city,
                'zip': customer.zip,
                'email': customer.email,
                'mobile': customer.mobile,
                'phone': customer.phone,
                'type': type
            })

        address = {
            'logo': configs.branch_id.company_id.logo_web,
            'company_name': configs.company_id.name,
            'company_street1': configs.company_id.street,
            'company_street2': configs.company_id.street2,
            'company_city': configs.company_id.city,
            'company_zip': configs.company_id.zip,
            'company_country': configs.company_id.country_id.name
        }
        return {
            'customer_history': customer_history,
            'address': address
        }

    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        if data['customer_ids']:
            customer_ids = self.env['res.partner'].browse(data['customer_ids'])
        else:
            customer_ids = self.env['res.partner'].search([])
        configs = self.env['pos.config'].browse(data['pos_config_ids'])
        data.update(self.get_credit_details(data['date_start'], data['date_stop'], customer_ids, configs, data['type']))
        return data
