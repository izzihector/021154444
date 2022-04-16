from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
from datetime import timedelta
from datetime import datetime

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class StockReport(models.TransientModel):
    _name = "wizard.customer.credit"
    _description = "See Customer Credit"

    start_date = fields.Datetime(required=True, default=fields.Datetime.now())
    end_date = fields.Datetime(required=True, default=fields.Datetime.now())
    customer = fields.Many2many('res.partner', string="Customer", help="List of Customer and Vendors")

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    def generate_xlsx_report(self):
        data = {
            'id': self.id,
            'model': self._name,
            'date_start': self.start_date,
            'date_stop': self.end_date,
            'customer_ids': self.customer.ids
        }

        return {
            'type': 'ir.actions.report',
            'data': {'model': 'wizard.customer.credit',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Customer Credit',
                     },
            'report_type': 'pos_xlsx'
        }

    def get_credit_details(self, date_start=False, date_stop=False, customer_ids=False, configs=False, session_ids=False):

        date_start_format = fields.Datetime.from_string(date_start).date()
        date_end_format = fields.Datetime.from_string(date_stop).date()

        data = []
        total_credit_limit = 0.0
        total_credit_consumed = 0.0
        total_credit_remaining = 0.0
        total_credit_purchase = 0.0
        total_credit_return = 0.0
        total_paid_amount = 0.0
        i = 1

        if date_start:
            date_start = fields.Datetime.from_string(date_start).replace(hour=0, minute=0, second=0)
        else:
            date_start = date_start + timedelta(days=1, seconds=-1)

        if date_stop:
            date_stop = fields.Datetime.from_string(date_stop).replace(hour=23, minute=59, second=59)
        else:
            date_stop = date_start + timedelta(days=1, seconds=-1)

        domain = []
        if customer_ids:
            domain = [('id', 'in', customer_ids)]
        customer = self.env['res.partner'].search(domain, order="barcode desc")
        for cus in customer:
            pos_order = self.env['pos.order'].search([('partner_id', '=', cus.id),
                                                      ('date_order', '>=', fields.Datetime.to_string(date_start)),
                                                      ('date_order', '<=', fields.Datetime.to_string(date_stop))])

            # credit_history = self.env['credit.history'].search([('pos_order_id', '=', pos_order.ids)]).read()
            # print('credit_history', credit_history)
            # print('credit length', len(credit_history))

            due_amt = 0
            total_purchase = 0
            total_paid = 0

            # if len(credit_history) >= 1:
            #     print("used_credit_amount", credit_history[0]['used_credit_amount'])
            #     # due_amt = credit_history.used_credit_amount

            for pos_ord in pos_order:
                for payment in pos_ord.payment_ids:
                    if payment.payment_method_id.name == "Credit" or payment.payment_method_id.name == "credit":
                        due_amt += payment.amount
                        total_purchase += pos_ord.amount_total
                        total_paid += pos_ord.amount_paid

            if due_amt > 0:
                credit_consumed = round(due_amt, 2)
                credit_remaining = round(cus.custom_credit, 2)
                total_credit_purchase += total_purchase
                total_credit_consumed = total_credit_consumed + credit_consumed
                total_credit_remaining = total_credit_remaining + credit_remaining
                total_credit_limit = total_credit_limit + cus['credit_limit']
                total_paid_amount += total_paid

                data.append({
                    'SL': i,
                    'phone': cus['phone'],
                    'name': cus['name'],
                    'total_purchase': total_purchase,
                    'total_paid': total_paid,
                    'total_due': credit_consumed,
                    'credit_remaining': credit_remaining,
                    'credit_limit': cus['credit_limit'],
                })
                i = i + 1
        return {
            'date_start': str(date_start_format),
            'date_end': str(date_end_format),
            'current_date': fields.Datetime.now(),
            'data': data,
            'total_credit': round(total_credit_consumed, 2),
            'total_remaining': round(total_credit_remaining, 2),
            'total_limit': round(total_credit_limit, 2),
            'total_purchase': round(total_credit_purchase, 2),
            'total_paid': round(total_paid_amount, 2),
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('pos customer credit report')
        data = dict(data or {})
        customers = self.env['res.partner'].browse(data['customer_ids'])
        configs = self.env['pos.config'].search([])
        data.update(self.get_credit_details(data['date_start'], data['date_stop'], customers.ids, configs))
        comp = self.env.user.company_id.name

        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter','bold': True })
        format3 = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'bold': True})
        format32 = workbook.add_format({'font_size': 11, 'align': 'vcenter'})
        title = workbook.add_format({'font_size': 16, 'align': 'center', 'bold': True})


        date_start = fields.Datetime.from_string(data['date_start']).replace(hour=0, minute=0, second=0)
        date_end = fields.Datetime.from_string(data['date_end']).replace(hour=0, minute=0, second=0)

        sheet.merge_range(0, 2, 0, 5, comp, title)
        sheet.set_column(0, 6, len(comp))

        data1_len = len(data['date_start'])
        data2_len = len(data['date_end'])
        sheet.write(2, 0, 'Date', format2)
        sheet.write(2, 1, data['date_start'], format2)
        sheet.set_column(2, 1, data1_len)
        sheet.write(2, 2, 'To', format2)
        sheet.write(2, 3, data['date_end'], format2)
        sheet.set_column(2, 3, data2_len)

        sheet.write(3, 0, "SL", format3)
        sheet.write(3, 1, "Name", format3)
        sheet.set_column(3, 1, len('Name'))
        sheet.write(3, 2, "Phone", format3)
        sheet.set_column(3, 2, len('Phone'))
        sheet.write(3, 3, "Total Purchase", format3)
        sheet.set_column(3, 3, len('Total Purchase'))
        sheet.write(3, 4, "Total Paid", format3)
        sheet.set_column(3, 4, len('Total Paid'))
        sheet.write(3, 5, "Total Credit", format3)
        sheet.set_column(3, 5, len('Total Credit'))
        sheet.write(3, 6, "Credit Limit", format3)
        sheet.set_column(3, 5, len('Credit Limit'))

        row = 4
        name_len = 0
        phone_len = 0


        for table_data in data['data']:
            col = 0
            sheet.write(row, col, table_data['SL'], format32)
            col += 1
            sheet.write(row, col, table_data['name'], format32)
            col += 1
            sheet.write(row, col, table_data['phone'], format32)
            col += 1
            sheet.write(row, col, table_data['total_purchase'], format32)
            col += 1
            sheet.write(row, col, table_data['total_paid'], format32)
            col += 1
            sheet.write(row, col, table_data['total_due'], format32)
            col += 1
            sheet.write(row, col, table_data['credit_limit'], format32)

            row += 1

            if table_data['name']:
                if name_len < len(table_data['name']):
                    name_len = len(table_data['name'])

            if table_data['phone']:
                if phone_len < len(table_data['phone']):
                    phone_len = len(table_data['phone'])

        sheet.write(row, 2, 'Total', format1)
        sheet.write(row, 3, data['total_purchase'], format3)
        sheet.write(row, 4, data['total_paid'], format3)
        sheet.write(row, 5, data['total_credit'], format3)
        sheet.write(row, 6, data['total_limit'], format3)

        if name_len > 0:
            sheet.set_column(row, 1, name_len)
        if phone_len > 0:
            sheet.set_column(row, 2, phone_len)


        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
