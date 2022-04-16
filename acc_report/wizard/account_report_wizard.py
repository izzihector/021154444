# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from io import BytesIO
import base64

try:
    import xlwt
except ImportError:
    xlwt = None


class AccountReportWizard(models.TransientModel):
    _name = 'account.report.wizard'
    _description = 'Account Report Wizard'

    datas = fields.Binary('File')
    report_type = fields.Selection([
                                    ('ma', 'MA'),
                                    ('ragio', 'Ragio'),
                                    ('cargo', 'Cargo'),
                                    # ('region', 'Region'),
                                   ], string="Report Type", default="ma")

    def _get_account_move_entry(self, accounts):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """
        acc_ids = self.env.context.get('account_ids')
        if acc_ids:
            accounts = accounts.filtered(lambda a: a.id in acc_ids)
        # if self.env.context.get('account_ids'):
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}
        init_balance = False
        display_account = 'all'

        sql_sort = 'l.date, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.analytic_account_id, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            analytic_bal = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
                if line.get('analytic_account_id'):
                    analytic_acc = self.env['account.analytic.account'].browse(line.get('analytic_account_id'))
                    analytic_bal = analytic_acc.balance
                    row['analytic_bal'] = analytic_bal
            row['balance'] += balance
            row['acc_id'] = row['account_id']
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            # currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['account_id'] = account.id
            res['code'] = account.code
            res['name'] = account.name
            res['ma'] = account.ma
            res['cargo'] = account.cargo
            res['ragio'] = account.ragio
            res['move_lines'] = move_lines[account.id]
            print ("\n\n\n-----------", account.id)
            res['overhead'] = self.get_overhead_value(res['move_lines'], self.report_type)
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            del res['move_lines']
            # if display_account == 'movement' and res.get('move_lines'):
            #     account_res.append(res)
            # if display_account == 'not_zero' and not currency.is_zero(res['balance']):
            #     account_res.append(res)

        return account_res

    
    def get_overhead_value(self, movelines, report_type):
        # overhead_data = {}
        total = 0.0
        if movelines:
            analytic_ids = []
            for line in movelines:
                print ("LINEEEEEEEEEEEEEEEEEEEEEEE", line.get('analytic_account_id'))
                if line.get('analytic_account_id') not in analytic_ids:
                    analytic_ids.append(line.get('analytic_account_id'))
            print ("analytic_ids::::::::::::::::", analytic_ids)
            for acc in analytic_ids:
                acc_id = self.env['account.analytic.account'].browse(acc)
                if acc_id.cost_group_id and acc_id.cost_group_id.is_overhead:
                    balance = 0.0
                    for line in movelines:
                        if line.get('analytic_account_id') == acc:
                            balance += line['debit'] - line['credit']
                    if report_type == 'ma' and acc_id.ma > 0:
                        total = balance * acc_id.ma / 100
                    if report_type == 'cargo' and acc_id.cargo > 0:
                        total = balance * acc_id.cargo / 100
                    if report_type == 'ragio' and acc_id.ragio > 0:
                        total = balance * acc_id.ragio / 100
        return total

    
    def get_income_data(self):
        income_dict = {}
        for grp in self.env['total.group'].search([]):
            acc_list = []
            for income in self.env['account.account'].search([('group_type', '=', 'income'), ('total_group_id', '=', grp.id)]):
                income_datas = self._get_account_move_entry(income)
                acc_list.append(income_datas[0])
                income_dict[grp.name] = acc_list
        return income_dict

    
    def get_expense_data(self):
        expense_dict = {}
        for grp in self.env['total.group'].search([]):
            acc_list = []
            for expense in self.env['account.account'].search([('group_type', '=', 'expense'), ('total_group_id', '=', grp.id)]):
                expense_datas = self._get_account_move_entry(expense)
                acc_list.append(expense_datas[0])
                expense_dict[grp.name] = acc_list
        return expense_dict

    
    def get_other_income_data(self):
        other_income_dict = {}
        for grp in self.env['total.group'].search([]):
            acc_list = []
            for other_income in self.env['account.account'].search([('group_type', '=', 'other_income'), ('total_group_id', '=', grp.id)]):
                other_income_datas = self._get_account_move_entry(other_income)
                acc_list.append(other_income_datas[0])
                other_income_dict[grp.name] = acc_list
        return other_income_dict

    
    def get_other_expense_data(self):
        other_expense_dict = {}
        for grp in self.env['total.group'].search([]):
            acc_list = []
            for other_expense in self.env['account.account'].search([('group_type', '=', 'other_expense'), ('total_group_id', '=', grp.id)]):
                other_expense_datas = self._get_account_move_entry(other_expense)
                acc_list.append(other_expense_datas[0])
                other_expense_dict[grp.name] = acc_list
        return other_expense_dict

    
    def get_ma_account_record(self, workbook):
        worksheet = workbook.add_sheet('Mid Atlantic - Chart')
        header_bold = xlwt.easyxf("font: bold on, height 150;")
        row = 0
        col = 0
        worksheet.write(row, col, _('SOORT'), header_bold)
        col += 1
        worksheet.write(row, col, _('OMSCHRYVING'), header_bold)
        col += 1
        worksheet.write(row, col, _('M.A.OPER.'), header_bold)
        col += 1
        worksheet.write(row, col, _('OVERHEAD'), header_bold)
        col += 1
        worksheet.write(row, col, _('TOTAAL'), header_bold)
        col += 1
        income_datas = self.get_income_data()
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
        style2 = xlwt.easyxf('pattern: pattern solid, fore_colour green;')
        if income_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in income_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'ma' and data.get('ma') > 0.0:
                        balance = data.get('ma') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTAAL OPBRENGSTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

        expense_datas = self.get_expense_data()
        if expense_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in expense_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'ma' and data.get('ma') > 0.0:
                        balance = data.get('ma') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTAAL KOSTEN EXCL. OVERHEAD'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

        other_income_datas = self.get_other_income_data()
        if other_income_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in other_income_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'ma' and data.get('ma') > 0.0:
                        balance = data.get('ma') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTALE EXPLOITATIEKOSTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

        other_expense_datas = self.get_other_expense_data()
        if other_expense_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in other_expense_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'ma' and data.get('ma') > 0.0:
                        balance = data.get('ma') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTALE FINANCIELE BATEN EN LASTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

    
    def get_ragio_account_record(self, workbook):
        worksheet = workbook.add_sheet('Ragio - Chart')
        header_bold = xlwt.easyxf("font: bold on, height 150;")
        row = 0
        col = 0
        worksheet.write(row, col, _('SOORT'), header_bold)
        col += 1
        worksheet.write(row, col, _('OMSCHRYVING'), header_bold)
        col += 1
        worksheet.write(row, col, _('REGIO OPER.'), header_bold)
        col += 1
        worksheet.write(row, col, _('OVERHEAD'), header_bold)
        col += 1
        worksheet.write(row, col, _('TOTAAL'), header_bold)
        col += 1
        income_datas = self.get_income_data()
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
        style2 = xlwt.easyxf('pattern: pattern solid, fore_colour green;')
        if income_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in income_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'ragio' and data.get('ragio') > 0.0:
                        balance = data.get('ragio') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTAAL OPBRENGSTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1


        expense_datas = self.get_expense_data()
        if expense_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in expense_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'ragio' and data.get('ragio') > 0.0:
                        balance = data.get('ragio') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTAAL KOSTEN EXCL. OVERHEAD'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

        other_income_datas = self.get_other_income_data()
        if other_income_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in other_income_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'ragio' and data.get('ragio') > 0.0:
                        balance = data.get('ragio') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTALE EXPLOITATIEKOSTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

        other_expense_datas = self.get_other_expense_data()
        if other_expense_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in other_expense_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'ragio' and data.get('ragio') > 0.0:
                        balance = data.get('ragio') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTALE FINANCIELE BATEN EN LASTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

    
    def get_cargo_account_record(self, workbook):
        worksheet = workbook.add_sheet('Cargo - Chart')
        header_bold = xlwt.easyxf("font: bold on, height 150;")
        row = 0
        col = 0
        worksheet.write(row, col, _('SOORT'), header_bold)
        col += 1
        worksheet.write(row, col, _('OMSCHRYVING'), header_bold)
        col += 1
        worksheet.write(row, col, _('CARGO OPER.'), header_bold)
        col += 1
        worksheet.write(row, col, _('OVERHEAD'), header_bold)
        col += 1
        worksheet.write(row, col, _('TOTAAL'), header_bold)
        col += 1
        income_datas = self.get_income_data()
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
        style2 = xlwt.easyxf('pattern: pattern solid, fore_colour green;')
        if income_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in income_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'cargo' and data.get('cargo') > 0.0:
                        balance = data.get('cargo') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTAAL OPBRENGSTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1


        expense_datas = self.get_expense_data()
        if expense_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in expense_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'cargo' and data.get('cargo') > 0.0:
                        balance = data.get('cargo') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTAAL KOSTEN EXCL. OVERHEAD'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

        other_income_datas = self.get_other_income_data()
        if other_income_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in other_income_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'cargo' and data.get('cargo') > 0.0:
                        balance = data.get('cargo') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTALE EXPLOITATIEKOSTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

        other_expense_datas = self.get_other_expense_data()
        if other_expense_datas:
            row += 1
            total = 0.0
            total_overhead = 0.0
            for key, value in other_expense_datas.items():
                key_total = 0.0
                balance = 0.0
                over_head = 0.0
                for data in value:
                    overhead = data.get('overhead',0.0)
                    over_head += overhead
                    if self.report_type == 'cargo' and data.get('cargo') > 0.0:
                        balance = data.get('cargo') * data.get('balance') / 100
                    key_total += balance
                    col = 0
                    worksheet.write(row, col, data.get('code', ''))
                    col += 1
                    worksheet.write(row, col, data.get('name', ''))
                    col += 1
                    worksheet.write(row, col, balance)
                    col += 1
                    worksheet.write(row, col, overhead)
                    col += 1
                    worksheet.write(row, col, overhead + balance)
                    row += 1
                col = 1
                worksheet.write(row, col-1, '', style1)
                worksheet.write(row, col, key, style1)
                col += 1
                worksheet.write(row, col, key_total)
                col += 1
                worksheet.write(row, col, over_head)
                col += 1
                worksheet.write(row, col, key_total + over_head, style1)
                row += 2
                total += key_total
                total_overhead += over_head
            col = 1
            worksheet.write(row, col-1, '', style2)
            worksheet.write(row, col, _('TOTALE FINANCIELE BATEN EN LASTEN'), style2)
            col += 1
            worksheet.write(row, col, total)
            col += 1
            worksheet.write(row, col, total_overhead)
            col += 1
            worksheet.write(row, col, total + total_overhead, style2)
            row += 1

    
    def get_region_break_record(self, workbook):
        worksheet = workbook.add_sheet('Region Break')
        header_bold = xlwt.easyxf("font: bold on;")
        passage_1 = [
                 'PASSAGE', 'VRACHT', 'POST', 'OVERBAGAGE', 'CHARTERS REGIO & TUI', 'COMMISSIES',
                 'OPBRENGST TUI SAMENWERKING', 'OPBRENGST TERMINAL FEE', 'VRIJVAL VERVOERSVERPLICHTING', 'FUEL SURCHARGE & SECURITY', 'OVERIGE OPBRENGSTEN']
        doc = [
                 'DAGG/HOTEL, COCKP & CABINCREW', 'RESERVERINGS KOSTEN', 'ONDERHOUD EN REPARATIE', 'MAINTENANCE RESERVES', 'ENGINE LEASE', 'MANAGEMENT FEE BRANDSTOF', 'HUURKOSTEN (AOG)',
                 'LANDING', 'HANDLING', 'CATERING/INFLIGHT', 'COMMUNICATIE', 'VERTRAGINGSKOSTEN', 'OV DIVERSE EXPLOITATIE KOSTEN', 'OV EXPLOITATIE KOSTEN SABAKU CL']
        sub_foc = ['VLIEGTUIG ONDERHOUD', 'ASSURANTIE PREMIE', 'ONDERHOUD DOOR DERDEN', 'HUURKOSTEN (LEASE)', 'VOORZIENING C-CHECK', 'MAINTENANCE RESERVES']

        foc = ['CREW KOSTEN (FIX)', 'DIRECTORAAT OPERATIONELE ZAKEN']

        vest = ['MIAMI', 'CURACAO', 'ARUBA', '(CAY) BELEM', 'GUYANA', 'TRINIDAD', 'NEDERLAND']
        row = 0
        col = 0
        worksheet.set_panes_frozen(True)  # frozen headings instead of split panes
        worksheet.set_vert_split_pos(col+1)  # in general, freeze after last heading row
        worksheet.set_remove_splits(True)
        # Passage_1
        for r1 in passage_1:
            worksheet.write(row, col, r1)
            row += 1
        col = 0
        # Total Passage_1
        worksheet.write(row, col, _('NETTO INKOMSTEN'), header_bold)
        row += 2
        # Start DOC
        col = 0
        worksheet.write(row, col, _('DIRECT OPERATING COSTS'), header_bold)
        row += 1
        col = 0
        for r2 in doc:
            worksheet.write(row, col, r2)
            row += 1
        col = 0
        # Sub Total DOC
        worksheet.write(row, col, _('SUB TOTAAL DOC'), header_bold)
        row += 1
        # Start FUEL
        col = 0
        worksheet.write(row, col, _('BRANDSTOFKOSTEN'), header_bold)
        row += 1
        # Total Doc & Fuel
        col = 0
        worksheet.write(row, col, _('TOTAAL DOC & FUEL'), header_bold)
        row += 2
        # Start Sub FOC & FOC
        col = 0
        worksheet.write(row, col, _('FIXED OPERATING COSTS'), header_bold)
        row += 1
        col = 0
        for r3 in sub_foc:
            worksheet.write(row, col, r3)
            row += 1
        # Sub Total FOC
        col = 0
        worksheet.write(row, col, _('SUB TOTAAL FOC'), header_bold)
        row += 2
        col = 0
        for r4 in foc:
            worksheet.write(row, col, r4)
            row += 1
        # Total Doc & Fuel
        col = 0
        worksheet.write(row, col, _('TOTAAL FOC'), header_bold)
        row += 2
        # Strat VESTIGINGSKOSTEN
        col = 0
        worksheet.write(row, col, _('VESTIGINGSKOSTEN'), header_bold)
        row += 2
        col = 0
        for r5 in vest:
            worksheet.write(row, col, r5)
            row += 1
        # Sub Total VESTIGINGSKOSTEN
        col = 0
        worksheet.write(row, col, _('SUB TOTAAL VESTIGINGSKOSTEN'), header_bold)
        row += 1
        col = 0
        worksheet.write(row, col, _('OVERIGE VERKOOPKOSTEN PBM'))
        row += 1
        col = 0
        worksheet.write(row, col, _('TOTAL VESTIGINGS & VERKOOPKN'), header_bold)
        row += 1
        col = 0
        worksheet.write(row, col, _('SAMENWERKINGSKOSTEN TUI'))
        row += 1
        col = 0
        worksheet.write(row, col, _('TOTAAL KOSTEN EXCL. OVERHEAD'), header_bold)
        row += 1
        col = 0
        worksheet.write(row, col, _('OVERHEAD'))
        row += 1
        col = 0
        worksheet.write(row, col, _('TOTAAL KOSTEN INCL. OVERHEAD'), header_bold)
        row += 2
        # RESULTAAT
        col = 0
        worksheet.write(row, col, _('RESULTAAT'), header_bold)
        row += 2
        # AANTAL VLUCHTEN ENKEL
        col = 0
        worksheet.write(row, col, _('AANTAL VLUCHTEN ENKEL'), header_bold)
        row += 2
        # AANTAL VLUCHTEN RETOUR
        col = 0
        worksheet.write(row, col, _('AANTAL VLUCHTEN RETOUR'), header_bold)
        row += 2
        # AANTAL BLOKUREN
        col = 0
        worksheet.write(row, col, _('AANTAL BLOKUREN'), header_bold)

        row = 0
        col += 1
        worksheet.write(row, col, int(2000))
        row += 1
        worksheet.write(row, col, int(2000))
        row += 1
        worksheet.write(row, col, int(2000))

    
    def download_excel_file(self):
        workbook = xlwt.Workbook()
        if self.report_type == 'ma':
            name = 'Mid Atlantic - Chart'
            self.get_ma_account_record(workbook)
        if self.report_type == 'ragio':
            name = 'Region - Chart'
            self.get_ragio_account_record(workbook)
        if self.report_type == 'cargo':
            name = 'Cargo - Chart'
            self.get_cargo_account_record(workbook)
        # if self.report_type == 'region':
        #     name = 'Region - Break'
        #     self.get_region_break_record(workbook)

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        report_data_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'datas': report_data_file})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=account.report.wizard&field=datas&download=true&id=%s&filename=%s.xls' % (self.id, name),
            'target': 'new',
            }
