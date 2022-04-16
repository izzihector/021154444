# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
# from odoo.addons.mail.wizard.mail_compose_message import _reopen
from io import BytesIO
import base64

try:
    import xlwt
except ImportError:
    xlwt = None


class AccountCostCenter(models.TransientModel):
    _name = 'account.cost.center'
    _description = 'Account Cost center'

    datas = fields.Binary('File')

    
    def download__excel_file(self):
        cost_group_data = self.env['cost.group'].search([('is_overhead', '=', False)])
        account_obj = self.env['account.analytic.account']
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("COST CENTER", cell_overwrite_ok=True)
        header_bold = xlwt.easyxf("font: bold on, height 150;")

        row = 0
        col = 0
        # sheet.write_merge(top_row, bottom_row, left_column, right_column, 'Long Cell')
        worksheet.write_merge(row, col, row, col + 7, 'ENCRYPTION OF THE COST CENTER PROCES', header_bold)
        row += 2
        col = 0
        worksheet.write(row, col, _("COST CENTER"), header_bold)
        col += 1
        worksheet.write(row, col, _("DEPARTMENT"), header_bold)
        col += 1
        worksheet.write(row, col, _("MA"), header_bold)
        col += 1
        worksheet.write(row, col, _("REGIO"), header_bold)
        col += 1
        worksheet.write(row, col, _("CARGO"), header_bold)
        col += 1
        worksheet.write(row, col, _("TOTAL"), header_bold)
        col += 2
        worksheet.write(row, col, _("PROCES FLOW"), header_bold)

        row += 2
        col = 0
        for cost in cost_group_data:
            row += 1
            for acc in account_obj.search([('cost_group_id', '=', cost.id)]):
                col = 0
                worksheet.write(row, col, _(acc.code))
                col += 1
                worksheet.write(row, col, _(acc.name))
                col += 1
                ma = ""
                if acc.ma > 0.0:
                    ma = str(acc.ma) + " %"
                worksheet.write(row, col, ma)
                col += 1
                ragio = ""
                if acc.ragio > 0.0:
                    ragio = str(acc.ragio) + " %"
                worksheet.write(row, col, ragio)
                col += 1
                cargo = ""
                if acc.cargo > 0.0:
                    cargo = str(acc.cargo) + " %"
                worksheet.write(row, col, cargo)
                col += 1
                worksheet.write(row, col, _(acc.cargo + acc.ma + acc.ragio) + ' %' or '')
                col += 2
                worksheet.write(row, col, _(acc.process_flow_id.name))
                row += 1
            col = 0
            worksheet.write(row, col, _("Total"))
            col += 1
            worksheet.write(row, col, _(cost.name), header_bold)
            row += 2
        overhead_cost_data = self.env['cost.group'].search([('is_overhead', '=', True)])
        for overhead_cost in overhead_cost_data:
            row += 1
            for acc_cost in account_obj.search([('cost_group_id', '=', overhead_cost.id)]):
                col = 0
                worksheet.write(row, col, _(acc_cost.code))
                col += 1
                worksheet.write(row, col, _(acc_cost.name))
                col += 1
                ma = ""
                ma = str(acc_cost.ma) + " %"
                worksheet.write(row, col, ma)
                col += 1
                ragio = ""
                if acc_cost.ragio > 0.0:
                    ragio = str(acc_cost.ragio) + " %"
                worksheet.write(row, col, ragio)
                col += 1
                cargo = ""
                if acc_cost.cargo > 0.0:
                    cargo = str(acc_cost.cargo) + " %"
                worksheet.write(row, col, cargo)
                col += 1
                worksheet.write(row, col, _(acc_cost.cargo + acc_cost.ma + acc_cost.ragio) + ' %' or '')
                col += 2
                worksheet.write(row, col, _(acc_cost.process_flow_id.name))
                row += 1
            col = 0
            worksheet.write(row, col, _("Total"))
            col += 1
            worksheet.write(row, col, _(overhead_cost.name), header_bold)
            row += 2
        for no_group_acc in account_obj.search([('cost_group_id', '=', False)]):
            col = 0
            worksheet.write(row, col, _(no_group_acc.code))
            col += 1
            worksheet.write(row, col, _(no_group_acc.name))
            col += 1
            ma = ""
            if no_group_acc.ma > 0.0:
                ma = str(no_group_acc.ma) + " %"
            worksheet.write(row, col, ma)
            col += 1
            ragio = ""
            if no_group_acc.ragio > 0.0:
                ragio = str(no_group_acc.ragio) + " %"
            worksheet.write(row, col, ragio)
            col += 1
            cargo = ""
            if no_group_acc.cargo > 0.0:
                cargo = str(no_group_acc.cargo) + " %"
            worksheet.write(row, col, cargo)
            col += 1
            worksheet.write(row, col, _(no_group_acc.cargo + no_group_acc.ma + no_group_acc.ragio) + ' %' or '')
            col += 2
            worksheet.write(row, col, _(no_group_acc.process_flow_id.name))
            row += 1
        row += 2
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        report_data_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'datas': report_data_file})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=account.cost.center&field=datas&download=true&id=%s&filename=cost_center.xls' % (self.id),
            'target': 'new',
            }
