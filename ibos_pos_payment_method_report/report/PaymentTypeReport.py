from odoo import api, fields, models

class ReportTimesheet(models.AbstractModel):
    _name = 'report.ibos_pos_payment_method_report.report_payment_type'
    _description = 'Timesheet Report'

    def get_payment_method(self, docs, data):
        # print("Data", data)
        # print("Doc doc", docs)
        dict_pay_type = []
        total = 0
        for payment_method in docs.ids:
            record = self.env['pos.payment'].search([('payment_method_id', '=', payment_method), ('payment_date', '>=', data['from_date']), ('payment_date', '<=', data['to_date'])])
            print("record with date", record)

            method_val = 0
            method_name = ""
            if record:
                method_name = record.payment_method_id.name
                for rec in record:
                    print("This loop work")
                    method_val += rec.amount
                    total += rec.amount
            else:
                get_method_payment = self.env['pos.payment.method'].search([('id', '=', payment_method)])
                print("get_method_payment:", get_method_payment)
                if get_method_payment:
                    method_name = get_method_payment.name
            vals = {
                'name': method_name,
                'value': method_val,
            }

            dict_pay_type.append(vals)

        vals_total = {
            'name': "Total",
            'value': total,
        }
        dict_pay_type.append(vals_total)
        return dict_pay_type

    @api.model
    def _get_report_values(self, docids, data):
        docs = self.env['pos.sales.report.wizard'].browse(data['payment_method_id'])
        payment_value = self.get_payment_method(docs, data)
        return {
            'doc_ids': self.ids,
            'docs': docs,
            'payment_value': payment_value
        }
