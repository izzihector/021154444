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
from odoo.exceptions import UserError


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.common.report"
    _name = "account.report.general.ledger"
    _description = "General Ledger Report"

    display_account = fields.Selection([('all', 'All'), ('movement', 'With movements'),
                                        ('not_zero', 'With balance is not equal to 0'), ],
                                       string='Display Accounts', required=True, default='movement')
    initial_balance = fields.Boolean(string='Include Initial Balances',
                                     help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.')
    sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner',
                                                       'Journal & Partner')], string='Sort by', required=True, default='sort_date')
    account_range_ids = fields.One2many(
        'account.range', 'report_id', string="Account Range")
    account_ids = fields.Many2many('account.account', string='Accounts')
    datas = fields.Binary('File')

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
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
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts}

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(
                date_from=self.date_from, date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace(
                'account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, 0.0 AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                NULL AS currency_id,\
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                '' AS partner_name\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace(
            'account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of
        # move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id,
            l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit,
            COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name, l.pnr as pnr,
            l.bedrsrd as bedrsrd, l.faktnr as faktnr, l.bedrusd as bedrusd, l.omschr as omschr,
            l.opercde as opercde, l.controlle as controlle, l.vlnr as vlnr, l.gallon as gallon, l.pax as pax,
            l.plcde as plcde, l.mandgn as mandgn, l.handl as handl, l.sdatum as sdatum, l.maalt as maalt,
            l.kstnpl6 as kstnpl6, l.kstnpl7 as kstnpl7, l.betrekdg as betrekdg, l.betrekmd as betrekmd,
            l.betrekjr as betrekjr, l.galprijs as galprijs, l.factdg as factdg, l.factmd as factmd, l.factjr as factjr,
            l.vltype as vltype, l.vltreg as vltreg
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s ''' + filters +
               ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref,
             l.name, m.name, c.symbol, p.name,
             l.pnr, l.bedrsrd, l.faktnr, l.bedrusd, l.omschr, l.opercde, l.controlle, l.vlnr, l.gallon, l.pax,
            l.plcde, l.mandgn, l.handl, l.sdatum, l.maalt,
            l.kstnpl6, l.kstnpl7, l.betrekdg, l.betrekmd,
            l.betrekjr , l.galprijs, l.factdg, l.factmd ORDER BY ''' + sql_sort)
        params = (tuple(accounts),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        accounts = self.env['account.account'].browse(accounts)
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
                res['faktnr'] = line['faktnr']
                res['pnr'] = line['pnr']
                res['omschr'] = line['omschr']
                res['controlle'] = line['controlle']
                res['bedrsrd'] = line['bedrsrd']
                res['bedrusd'] = line['bedrusd']
                res['opercde'] = line['opercde']
                res['vlnr'] = line['vlnr']
                res['gallon'] = line['gallon']
                res['plcde'] = line['plcde']
                res['handl'] = line['handl']
                res['maalt'] = line['maalt']
                res['pax'] = line['pax']
                res['mandgn'] = line['mandgn']
                res['sdatum'] = line['sdatum']
                res['kstnpl6'] = line['kstnpl6']
                res['kstnpl7'] = line['kstnpl7']
                res['galprijs'] = line['galprijs']
                res['betrekdg'] = line['betrekdg']
                res['betrekmd'] = line['betrekmd']
                res['betrekjr'] = line['betrekjr']
                res['factdg'] = line['factdg']
                res['factmd'] = line['factmd']
                res['factjr'] = line['factjr']
                res['vltype'] = line['vltype']
                res['vltreg'] = line['vltreg']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
        return account_res

    
    def download__excel_file(self):
        move_state = ['draft', 'posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(self.journal_ids.ids), self.date_from,
                    self.date_to, tuple(move_state), self.company_id.id)
        query = """
                SELECT move.id FROM account_move_line aml
                LEFT JOIN account_move move ON aml.move_id = move.id
                WHERE move.journal_id in %s
                AND move.date >= %s and move.date <= %s
                AND move.state in %s
                AND move.company_id = %s
        """
        result = self._cr.execute(query, arg_list)
        query_res = self._cr.dictfetchall()
        account_list = self.account_ids.ids
        ress = []
        for rec in self.account_range_ids:
            if rec.check_range:
                self._cr.execute("""
                SELECT id from account_account WHERE CAST(code AS INTEGER) between %s and %s and company_id = %s
                """ % (rec.from_acc_id.code, rec.to_acc_id.code, self.company_id.id))
                ress = [res[0] for res in self._cr.fetchall()]

        account_list = list(set(ress))
        if not account_list:
            raise UserError(_("No Account Found!"))
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("EDGAR SALES", cell_overwrite_ok=True)
        header_bold = xlwt.easyxf("font: bold on, height 150;")

        row = 0
        col = 0
        header_list = ["VESTCD", "DAGB", "STUKNR", "REGNR", "BOEKJR", "PER", "DAG", "MND", "JAAR", "GROOTB",
                       "KSTNPL", "FAKTNR", "PNRR", "OMSCHR", "CONTROLLE", "CURCD", "BEDRAG", "BEDRSRD",
                       "BEDRUSD", "OPERCDE", "VLNR", "GALLON", "PLCDE", "HANDL", "MAALT", "PAX", "MANDGN",
                       "SDATUM", "KSTNPL6", "KSTNPL7", "PERSNR", "PONR", "GALPRIJS", "BETREKDG", "BETREKMD",
                       "BETREKJR", "FACTDG", "FACTMD", "FACTJR", "VLTYPE", "VLTREG", "CRED", "DEB"]
        for header in header_list:
            worksheet.write(row, col, _(header), header_bold)
            col += 1
        move_lines = self._get_account_move_entry(
            account_list, self.initial_balance, self.sortby, self.display_account)

        for res in move_lines:
            row += 1
            col = 0
            for rec in res.get('move_lines'):
                row += 1
                col = 0
                worksheet.write(row, col, '')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, ' ')
                col += 1
                worksheet.write(row, col, rec['faktnr'] or '')
                col += 1
                worksheet.write(row, col, rec['pnr'] or '')
                col += 1
                worksheet.write(row, col, rec['omschr'] or '')
                col += 1
                worksheet.write(row, col, rec['controlle'] or '')
                col += 1
                worksheet.write(row, col, rec['currency_code'] or '')
                col += 1
                worksheet.write(row, col, rec['amount_currency'] or 0.0)
                col += 1
                worksheet.write(row, col, rec['bedrsrd'] or 0.0)
                col += 1
                worksheet.write(row, col, rec['bedrusd'] or 0.0)
                col += 1
                worksheet.write(row, col, rec['opercde'] or '')
                col += 1
                worksheet.write(row, col, rec['vlnr'] or '')
                col += 1
                worksheet.write(row, col, rec['gallon'] or 0.0)
                col += 1
                worksheet.write(row, col, rec['plcde'] or '')
                col += 1
                worksheet.write(row, col, rec['handl'] or '')
                col += 1
                worksheet.write(row, col, rec['maalt'] or '')
                col += 1
                worksheet.write(row, col, rec['pax'] or '')
                col += 1
                worksheet.write(row, col, rec['mandgn'] or '')
                col += 1
                worksheet.write(row, col, rec['sdatum'] or '')
                col += 1
                worksheet.write(row, col, rec['kstnpl6'] or '')
                col += 1
                worksheet.write(row, col, rec['kstnpl7'] or '')
                col += 1
                worksheet.write(row, col, '')
                col += 1
                worksheet.write(row, col, '')
                col += 1
                worksheet.write(row, col, rec['galprijs'] or 0.0)
                col += 1
                worksheet.write(row, col, rec['betrekdg'] or '')
                col += 1
                worksheet.write(row, col, rec['betrekmd'] or '')
                col += 1
                worksheet.write(row, col, rec['betrekjr'] or '')
                col += 1
                worksheet.write(row, col, rec['factdg'] or '')
                col += 1
                worksheet.write(row, col, rec['factmd'] or '')
                col += 1
                worksheet.write(row, col, rec['factjr'] or '')
                col += 1
                worksheet.write(row, col, rec['vltype'] or '')
                col += 1
                worksheet.write(row, col, rec['vltreg'] or '')
                col += 1
                worksheet.write(row, col, rec['credit'] or '')
                col += 1
                worksheet.write(row, col, rec['debit'] or '')
            row += 1
        row += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        report_data_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'datas': report_data_file})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=account.report.general.ledger&field=datas&download=true&id=%s&filename=general_+ledger.xls' % (self.id),
            'target': 'new',
        }


class AccountRange(models.TransientModel):

    _name = 'account.range'

    report_id = fields.Many2one('account.report.general.ledger')
    from_acc_id = fields.Many2one('account.account', 'From Account')
    to_acc_id = fields.Many2one('account.account', 'To Account')
    check_range = fields.Boolean('Check')
