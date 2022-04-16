# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from xlrd import open_workbook, XLRDError, XL_CELL_EMPTY, XL_CELL_BLANK
from odoo.exceptions import UserError, AccessError
from dateutil.parser import parse

# pip install xlrd==1.2.0

class ImportFile(models.Model):
    _name = 'slm.import.file'

    months = [("{:02d}".format(m), date(datetime.today().year, m, 1).strftime('%B').capitalize()) for m in range(1, 13)]
    years = [(str(y), str(y)) for y in range(2019, 2050)]
    rows = ['vestcd', 'dagb', 'stuknr', 'regnr', 'boekjr', 'per', 'dag', 'mnd', 'jaar', 'grootb', 'kstnpl', 'faktnr',
            'pnr', 'omschr', 'controle', 'curcd', 'bedrag', 'bedrsrd', 'bedrusd', 'opercde', 'vlnr', 'gallon', 'plcde',
            'handl', 'maalt', 'pax', 'mandgn', 'sdatum', 'kstnpl6', 'kstnpl7', 'persnr', 'ponr', 'galprijs', 'betrekdg',
            'betrekmd', 'betrekjr', 'factdg', 'factmd', 'factjr', 'vltype', 'vltreg', 'cred', 'deb']

    filename = fields.Char('File name')
    file = fields.Binary(string="File", required=True)
    year = fields.Selection(years, string='Year', default=lambda y: datetime.today().strftime('%Y'), required=True)
    month = fields.Selection(months, string='Month', default=lambda y: datetime.today().strftime('%m'), required=True)
    error = fields.Boolean('Error')
    row_ids = fields.One2many('slm.import.file.row', 'import_file_id', string='Import File rows', copy=True)
    sheet_ids = fields.One2many('slm.import.file.sheet', 'import_file_id', string='Import File Sheets', copy=True)
    error_ids = fields.One2many('slm.import.file.error', 'import_file_id', string='Import File Errors', copy=True)
    sheet_count = fields.Integer(compute='compute_sheet')
    category_id = fields.Many2one('slm.import.file.category', string='Category', ondelete="cascade", index=True,
                                  required=True, auto_join=True)
    state = fields.Selection(
        [('uploaded', 'Uploaded'), ('unbalanced', 'Unbalanced'), ('error', 'Error'), ('verified', 'Verified'),
         ('entry', 'Journal created'), ('posted', 'Posted')], string='Status', readonly=True, copy=False, default="uploaded")
    company = fields.Many2one('res.company', string='Company', ondelete="cascade", index=True,
                              required=True, auto_join=True, default=2)
    move_id = fields.Many2one('account.move', string='Journal Entry', ondelete="cascade", index=True,
                              required=False, auto_join=True)

    @api.depends('sheet_ids')
    def compute_sheet(self):
        for rec in self:
            rec.sheet_count = len(rec.sheet_ids)

    def name_get(self):
        return [
            (record.id, "{} {} {}".format(record.category_id.name, record.year, dict(self.months).get(record.month)))
            for record in self]

    @api.constrains('filename')
    def _check_filename(self):
        if self.file:
            if not self.filename:
                raise ValidationError(_("There is no file"))
            else:
                # Check the file's extension
                tmp = self.filename.split('.')
                ext = tmp[len(tmp) - 1]
                if ext not in ['xls', 'xlsx']:
                    raise ValidationError(_("The file must be a Excel file type"))
            try:
                open_workbook(file_contents=base64.decodebytes(self.file))
            except (XLRDError, Exception) as e:
                raise ValidationError(e)

    @api.model
    def create(self, values):
        # values['state'] = 'uploaded'
        # sheets = self._get_sheets(values['file'])
        # if sheets:
        #     values['sheet_ids'] = sheets
        res = super(ImportFile, self).create(values)
        # sheet_ids = [{'id': sheet.id, 'name': sheet.name} for sheet in res.sheet_ids]
        # print ("sheet_ids", sheet_ids)
        # # row_ids = self._import_rows(sheet_ids, values['month'], values['year'], values['file'])
        # # res.update({'row_ids': row_ids})
        # self._calculate_usd_amounts(res.id)
        # error_ids = self._get_errors(res)
        # res.update({'error_ids': error_ids})
        # balance = self._get_balance(res.id)
        # if int(balance) == 0 and not error_ids:
        #     res.update({'state': 'verified'})
        # elif not error_ids:
        #     res.update({'state': 'unbalanced'})
        # else:
        #     res.update({'state': 'error'})

        return res

    def read_file(self):
        sheets = False
        try:
            wb = open_workbook(file_contents=base64.decodebytes(self.file))
            sheets = [(0, 0, {'name': sheet_name, 'rows': wb.sheet_by_name(sheet_name).nrows}) for sheet_name in wb.sheet_names()]
        except Exception as e:
            raise UserError(_("Sorry, Your excel file does not match with our format " + str(e)))
        if sheets:
            self.sheet_ids = sheets
            self.write({'state': 'uploaded'})
            sheet_ids = [{'id': sheet.id, 'name': sheet.name} for sheet in self.sheet_ids]
            row_ids = self._import_rows(sheet_ids)
            self.update({'row_ids': row_ids})
            self._calculate_usd_amounts(self.id)
            error_ids = self._get_errors(self)
            self.update({'error_ids': error_ids})

            balance = self._get_balance(self.id)
            if int(balance) == 0 and not error_ids:
                self.update({'state': 'verified'})
            elif not error_ids:
                self.update({'state': 'unbalanced'})
            else:
                self.update({'state': 'error'})
        return True

    def write(self, values):
        res = super(ImportFile, self).write(values)
        return res

    def _get_sheets(self, file=None):
        print ("files", file)
        try:
            wb = open_workbook(file_contents=base64.decodebytes(file))
            # wb = open_workbook(file_contents=file)
            return [(0, 0, {'name': sheet_name, 'rows': wb.sheet_by_name(sheet_name).nrows})
                    for sheet_name in wb.sheet_names()]
        except Exception as e:
            raise UserError(_("Sorry, Your excel file does not match with our format " + str(e)))

    def _import_rows(self, sheets):
        month = self.month
        year = self.year
        file = self.file
        try:
            wb = open_workbook(file_contents=base64.decodebytes(file))
            # wb = open_workbook(file_contents=base64.b64decode(file))
            skipped_line_no = {}
            row_ids = []
            for sheet_dict in sheets:
                skip_header = True
                counter = 1
                sheet = wb.sheet_by_name(sheet_dict['name'])
                for row in range(sheet.nrows):
                    try:
                        if skip_header:
                            skip_header = False
                            counter = counter + 1
                            continue
                        row_dict = {}
                        for index, field in enumerate(self.rows):
                            if sheet.cell_type(row, index) not in (XL_CELL_EMPTY, XL_CELL_BLANK):
                                value = sheet.cell(row, index).value
                                if field in ['stunkr', 'regnr', 'grootb', 'kstnpl']:
                                    value = str(int(value))
                                row_dict[field] = value
                        file_date = parse("{}{}01".format(year, month))
                        last_file_date = self.last_day_of_month(file_date)

                        if not row_dict['mnd'] or not (isinstance(row_dict['mnd'], int) or isinstance(row_dict['mnd'], float)):
                            row_dict['mnd'] = last_file_date.month
                            row_dict['dag'] = last_file_date.day
                            row_dict['jaar'] = last_file_date.year
                        elif not row_dict['jaar'] or not (isinstance(row_dict['jaar'], int) or isinstance(row_dict['jaar'], float)):
                            row_dict['jaar'] = last_file_date.year
                        elif not row_dict['dag'] or not (isinstance(row_dict['mnd'], int) or isinstance(row_dict['mnd'], float)):
                            row_date = parse("{}{:02d}01".format(row_dict['jaar'], row_dict['mnd']))
                            last_row_date = self.last_day_of_month(row_date)
                            row_dict['dag'] = last_row_date.day
                        try:
                            if int(row_dict['deb']) == 0:
                                row_dict['deb'] = None
                        except (ValueError, KeyError):
                            pass

                        try:
                            if int(row_dict['cred']) == 0:
                                row_dict['cred'] = None
                        except (ValueError, KeyError):
                            pass

                        try:
                            row_dict['vlnr'] = str(int(row_dict['vlnr']))
                        except (ValueError, KeyError):
                            pass

                        row_dict['sheet_id'] = sheet_dict['id']
                        row_dict['number'] = row
                        row_ids.append((0, 0, row_dict))

                    except Exception as e:
                        skipped_line_no[str(counter)] = " - Value is not valid. " + str(e)
                        counter = counter + 1
                        continue
            return row_ids
        except Exception as e:
            raise UserError(_("Sorry, Your excel file does not match with our format" + str(e)))

    def last_day_of_month(self, date_file):
        if date_file.month == 12:
            return date_file.replace(day=31)
        return date_file.replace(month=date_file.month + 1, day=1) - timedelta(days=1)

    def _calculate_usd_amounts(self, id):
        query_update_rows = """
            UPDATE slm_import_file_row
            SET amount = T.amount
            FROM (SELECT SIFR.id,
                         CASE
                             WHEN bedrusd NOTNULL
                                 THEN BEDRUSD
                             ELSE
                                 CASE
                                     WHEN curcd NOTNULL AND curcd = 840
                                         THEN bedrag
                                     WHEN CURCD NOTNULL
                                         THEN bedrag / RCR.rate
                                     ELSE bedrag
                                     END
                             END
                             AS amount
                  FROM slm_import_file_row SIFR
                           JOIN res_currency RC ON (RC.currency_code = SIFR.curcd::VARCHAR)
                           LEFT JOIN res_currency_rate RCR ON
                      (RC.id = RCR.currency_id AND RCR.name = date_trunc('month', CONCAT(jaar, LPAD(mnd::text, 2, '0'),
                        LPAD(dag::text, 2, '0'))::DATE)::date)
                  WHERE SIFR.import_file_id = %s) AS T
            WHERE T.id = slm_import_file_row.id
        """
        self.env.cr.execute(query_update_rows, (id,))

        query_update_sheets = """
            UPDATE slm_import_file_sheet
            SET debit = T2.debit, credit = T2.credit, balance = T2.balance
            FROM
            (SELECT sheet_id, SUM(debit) as debit, sum(credit) as credit, round(sum(debit - credit)::decimal, 6) as balance
            FROM (SELECT SIFR.sheet_id,
                         CASE
                             WHEN bedrusd NOTNULL
                                 THEN
                                 CASE
                                     WHEN bedrusd >= 0
                                         THEN bedrusd
                                     ELSE 0 END
                             ELSE
                                 CASE
                                     WHEN bedrag >= 0
                                         THEN
                                         CASE
                                             WHEN curcd NOTNULL AND CURCD = 840
                                                 THEN ABS(bedrag)
                                             WHEN curcd NOTNULL
                                                 THEN bedrag / RCR.rate
                                             ELSE bedrag
                                             END
                                     ELSE 0
                                     END
                             END
                             AS debit,
                         CASE
                             WHEN bedrusd NOTNULL
                                 THEN
                                 CASE
                                     WHEN bedrusd < 0
                                         THEN ABS(bedrusd)
                                     ELSE 0
                                     END
                             ELSE
                                 CASE
                                     WHEN bedrag <= 0
                                         THEN
                                         CASE
                                             WHEN curcd NOTNULL AND curcd = 840
                                                 THEN ABS(bedrag)
                                             WHEN curcd NOTNULL
                                                 THEN ABS(bedrag) / RCR.rate
                                             ELSE ABS(bedrag)
                                             END
                                     ELSE 0
                                     END
                             END
                             AS credit
                  FROM slm_import_file_row SIFR
                           JOIN res_currency RC ON (RC.currency_code = SIFR.curcd::VARCHAR)
                           LEFT JOIN res_currency_rate RCR ON
                      (RC.id = RCR.currency_id AND
                       RCR.name = date_trunc('month', CONCAT(jaar, LPAD(mnd::text, 2, '0'), LPAD(dag::text, 2, '0'))::DATE)::date)
                  WHERE SIFR.import_file_id = %s) AS T
            GROUP BY sheet_id) AS T2
            WHERE slm_import_file_sheet.id = T2.sheet_id
        """
        self.env.cr.execute(query_update_sheets, (id,))

    def _get_errors(self, res):
        query_mandatory_analytic_accounts = """
            SELECT SIFR.id AS row_id, SIFR.sheet_id, SIFR.number, AAM.id as mandatory_id,
                string_agg(AAA_MANDATORY.code, ',') as "mandatory_accounts"
            FROM slm_import_file SIF
                JOIN slm_import_file_row SIFR ON (SIFR.import_file_id = SIF.id)
            JOIN account_account AA ON (AA.code = SIFR.grootb)
            JOIN account_analytic_account AAA ON (AAA.code = SIFR.kstnpl)
            JOIN account_analytic_mandatory AAM ON (AA.id = AAM.account_id)
            JOIN account_analytic_account_account_analytic_mandatory_rel AAAAAMR ON (AAM.id = AAAAAMR.account_analytic_mandatory_id)
            JOIN account_analytic_account AAA_MANDATORY ON (AAA_MANDATORY.id = AAAAAMR.account_analytic_account_id)
            WHERE SIF.id = %s
            AND AAA.id NOT IN (SELECT account_analytic_account_id
                                FROM account_analytic_account_account_analytic_mandatory_rel
                                WHERE account_analytic_mandatory_id = AAM.id)
            GROUP BY SIFR.grootb, SIFR.vlnr, SIFR.kstnpl, AAM.id, SIFR.id, SIF.id;
        """

        self.env.cr.execute(query_mandatory_analytic_accounts, (res.id,))
        mandatory_results = self.env.cr.dictfetchall()

        query_mandatory_vlnr = """
            SELECT DISTINCT SIFR.id AS row_id, SIFR.sheet_id, SIFR.number, AAM.id AS mandatory_id
            FROM slm_import_file SIF
                JOIN slm_import_file_row SIFR ON (SIFR.import_file_id = SIF.id)
            JOIN account_account AA ON (AA.code = SIFR.grootb)
            JOIN account_analytic_account AAA ON (AAA.code = SIFR.kstnpl)
            JOIN account_analytic_mandatory AAM ON (AA.id = AAM.account_id)
            JOIN account_analytic_account_account_analytic_mandatory_vlnr_rel AAAAAMVR ON (AAM.id = AAAAAMVR.account_analytic_mandatory_id)
            WHERE SIF.id = %s
            AND SIFR.vlnr ISNULL ;
        """
        self.env.cr.execute(query_mandatory_vlnr, (res.id,))
        vlnr_results = self.env.cr.dictfetchall()

        query_missing_accounts = """
            SELECT SIFR.id AS row_id, SIFR.sheet_id, SIFR.number, SIFR.grootb AS account
            FROM slm_import_file SIF
                JOIN slm_import_file_row SIFR ON (SIFR.import_file_id = SIF.id)
            LEFT JOIN account_account AA ON (SIFR.grootb = AA.code AND AA.company_id = %s)
            WHERE SIF.id= %s
            AND AA.id ISNULL;
        """
        self.env.cr.execute(query_missing_accounts, (res.company.id, res.id,))
        missing_accounts_results = self.env.cr.dictfetchall()

        query_curcd = """
            SELECT SIFR.id AS row_id, SIFR.sheet_id, SIFR.number,
                   CASE
                       WHEN SIFR.curcd NOTNULL
                           THEN 'CURCD not exists'
                       ELSE 'Missing CURCD'
                       END AS curcd_error
            FROM slm_import_file SIF
                     JOIN slm_import_file_row SIFR ON (SIFR.import_file_id = SIF.id)
                     LEFT JOIN res_currency RC ON (RC.currency_code = SIFR.curcd::VARCHAR)
            WHERE SIF.id = %s
              AND (SIFR.curcd IS NULL OR RC.currency_code IS NULL)
        """
        self.env.cr.execute(query_curcd, (res.id,))
        curcd_results = self.env.cr.dictfetchall()

        query_cred = """
            SELECT SIFR.id AS row_id, SIFR.sheet_id, SIFR.number, SIFR.cred
                FROM slm_import_file SIF
                JOIN slm_import_file_row SIFR ON (SIFR.import_file_id = SIF.id)
                LEFT JOIN res_partner RP on SIFR.cred = RP.name
                WHERE SIF.id = %s
                    AND SIFR.cred IS NOT NULL
                    AND RP.id IS NULL
        """
        self.env.cr.execute(query_cred, (res.id,))
        cred_results = self.env.cr.dictfetchall()

        query_deb = """
                    SELECT SIFR.id AS row_id, SIFR.sheet_id, SIFR.number, SIFR.deb
                        FROM slm_import_file SIF
                        JOIN slm_import_file_row SIFR ON (SIFR.import_file_id = SIF.id)
                        LEFT JOIN res_partner RP on SIFR.deb = RP.name
                        WHERE SIF.id = %s
                            AND SIFR.deb IS NOT NULL
                            AND RP.id IS NULL
                """
        self.env.cr.execute(query_deb, (res.id,))
        deb_results = self.env.cr.dictfetchall()
        errors = {}
        for row in mandatory_results:
            if row['row_id'] not in errors:
                errors[row['row_id']] = {'sheet_id': row['sheet_id'], 'row_id': row['row_id'],
                                         'row_number': row['number']}
            errors[row['row_id']]['analytic_account_required'] = row['mandatory_accounts']
            errors[row['row_id']]['mandatory_rule'] = row['mandatory_id']

        for row in vlnr_results:
            if row['row_id'] not in errors:
                errors[row['row_id']] = {'sheet_id': row['sheet_id'], 'row_id': row['row_id'],
                                         'row_number': row['number']}
            errors[row['row_id']]['vlnr_required'] = True
            errors[row['row_id']]['mandatory_rule'] = row['mandatory_id']

        for row in missing_accounts_results:
            if row['row_id'] not in errors:
                errors[row['row_id']] = {'sheet_id': row['sheet_id'], 'row_id': row['row_id'],
                                         'row_number': row['number']}
            errors[row['row_id']]['account'] = row['account']

        for row in curcd_results:
            if row['row_id'] not in errors:
                errors[row['row_id']] = {'sheet_id': row['sheet_id'], 'row_id': row['row_id'],
                                         'row_number': row['number']}
            errors[row['row_id']]['curcd_missing'] = row['curcd_error']

        for row in cred_results:
            if row['row_id'] not in errors:
                errors[row['row_id']] = {'sheet_id': row['sheet_id'], 'row_id': row['row_id'],
                                         'row_number': row['number']}
            errors[row['row_id']]['missing_creditor'] = row['cred']

        for row in deb_results:
            if row['row_id'] not in errors:
                errors[row['row_id']] = {'sheet_id': row['sheet_id'], 'row_id': row['row_id'],
                                         'row_number': row['number']}
            errors[row['row_id']]['missing_debtor'] = row['deb']

        errors_ids = []
        if errors:
            for row in errors.values():
                errors_ids.append((0, 0, row))
        return errors_ids

    def _get_balance(self, id):
        query = """SELECT SUM(amount) AS balance FROM slm_import_file_row WHERE import_file_id = %s""" % id
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        balance = results[0]['balance'] and results[0]['balance'] or 0.0
        return balance

    def action_balance(self):
        balance = self._get_balance(self.id)
        if balance > 0:
            credit = balance * -1
            debit = 0
        else:
            credit = 0
            debit = balance * -1

        file_date = parse("{}{}01".format(self.year, self.month))
        last_file_date = self.last_day_of_month(file_date)

        sheet = self.env['slm.import.file.sheet'].create(
            {'import_file_id': self.id, 'name': 'Unbalance adjustment', 'rows': 1, 'credit': credit, 'debit': debit,
             'balance': credit + debit})
        self.env['slm.import.file.row'].create({'import_file_id': self.id, 'sheet_id': sheet.id, 'number': 1,
                                                'amount': credit + debit, 'grootb': '940000', 'kstnpl': '60008',
                                                'dag': last_file_date.day, 'mnd': last_file_date.month,
                                                'jaar': last_file_date.year})
        if self.state != 'error':
            self.update({'state': 'verified'})

    def action_create(self, state='draft'):
        file_date = parse("{}{}01".format(self.year, self.month))
        last_file_date = self.last_day_of_month(file_date)
        amount = 0
        for sheet in self.sheet_ids:
            amount += sheet.debit
        name = self._get_name()

        insert_account_move = """
            INSERT INTO account_move(
                    name,
                    ref,
                    date,
                    journal_id,
                    currency_id,
                    state,
                    company_id,
                    amount_total,
                    move_type,
                    extract_state,
                    create_uid,create_date,write_uid,write_date)
                VALUES (%s,%s,%s,20,%s,%s,%s,%s,%s,%s,%s,now(),%s,now())
                RETURNING id;
        """
        params = (name, name, last_file_date, 2, state, self.company.id, amount, 'entry', 'no_extract_requested', self.env.user.id, self.env.user.id,)
        self.env.cr.execute(insert_account_move, params)
        result = self.env.cr.dictfetchall()
        account_move_id = result[0]['id']
        insert_account_move_line = """
            INSERT INTO
            account_move_line (
                name,debit,credit,balance,amount_currency,company_currency_id,currency_id,account_id,move_id,ref,
                journal_id,date_maturity,date,company_id,create_uid,create_date,write_uid,write_date,
                vestcd,dagb,stuknr,regnr,boekjr,per,dag,mnd,jaar,faktnr,pnr,omschr,controlle,curcd,bedrag,bedrsrd,
                bedrusd,opercde,vlnr,gallon,plcde,handl,maalt,pax,mandgn,sdatum,kstnpl6,kstnpl7,persnr,ponr,galprijs,
                betrekdg,betrekmd,betrekjr,factdg,factmd,factjr,vltype,vltreg,partner_id,analytic_account_id)
            SELECT
                %s,
                CASE
                    WHEN amount >= 0
                        THEN amount
                    ELSE 0
                END AS DEBIT,
                CASE
                    WHEN amount < 0
                        THEN ABS(amount)
                    ELSE 0
                  END AS CREDIT,
                amount AS BALANCE,
                BEDRUSD AS AMOUNT_CURRENCY,
                2, 2, AA.id AS ACCOUNT_ID, %s AS MOVE_ID, %s AS REF, 20,
                CONCAT(JAAR,LPAD(MND::text, 2, '0'),LPAD(DAG::text, 2, '0'))::DATE AS DATE_MATURITY,
                CONCAT(JAAR,LPAD(MND::text, 2, '0'),LPAD(DAG::text, 2, '0'))::DATE AS DATE,
                %s,
                2, now(), 2, now(), VESTCD, DAGB, STUKNR, REGNR, BOEKJR, PER, DAG, MND, JAAR, FAKTNR, PNR, OMSCHR, CONTROLE, CURCD, BEDRAG, BEDRSRD,
                BEDRUSD, OPERCDE, fl.id AS VLNR, GALLON, PLCDE, HANDL, MAALT,PAX, MANDGN, SDATUM, AAA_CC6.id AS KSTNPL6, AAA_CC7.id AS KSTNPL7, PERSNR,
                PONR, GALPRIJS, BETREKDG, BETREKMD, BETREKJR, FACTDG, FACTMD, FACTJR, VLTYPE, VLTREG,
                COALESCE(RP_CRED.id, RP_DEB.id) as PARTNER_ID,
                AAA.id AS ANALYTIC_ACCOUNT_ID
                FROM slm_import_file_row SIFR
                    LEFT JOIN account_account AA ON (AA.code = SIFR.GROOTB  AND AA.company_id=%s)
                    LEFT JOIN account_analytic_account AAA ON (AAA.code = SIFR.KSTNPL)
                    LEFT JOIN flight_list FL ON (FL.name = SIFR.VLNR)
                    LEFT JOIN account_analytic_account AAA_CC6 ON (AAA_CC6.code = SIFR.KSTNPL6)
                    LEFT JOIN account_analytic_account AAA_CC7 ON (AAA_CC7.code = SIFR.KSTNPL7)
                    LEFT JOIN res_partner RP_CRED ON (RP_CRED.name = SIFR.CRED)
                    LEFT JOIN res_partner RP_DEB ON (RP_DEB.name = SIFR.DEB)
                WHERE SIFR.import_file_id = %s
        """

        params = (name, account_move_id, name, self.company.id, self.company.id, self.id)
        self.env.cr.execute(insert_account_move_line, params)
        print ("account_move_id", account_move_id)
        self.update({
            'state': 'entry' if state == 'draft' else 'posted',
            'move_id': account_move_id
        })

    def action_create_post(self):
        self.action_create(state='posted')

    def action_post(self):
        self.move_id.update({'state': 'posted'})
        self.update({
            'state': 'posted',
        })

    def action_unpost(self):
        self.move_id.update({'state': 'draft'})
        self.update({
            'state': 'entry',
        })

    def action_remove(self):
        move_id = self.move_id.id
        self.update({
            'state': 'verified',
            'move_id': None
        })
        delete_move = """
                    DELETE FROM account_move WHERE id = %s
                """
        self.env.cr.execute(delete_move, (move_id,))

    def _get_name(self):
        file_date = parse("{}{}01".format(self.year, self.month))
        return "{} {}-{}".format(self.category_id.name, file_date.month, file_date.year)


class ImportFileRow(models.Model):
    _name = 'slm.import.file.row'

    import_file_id = fields.Many2one('slm.import.file', string='Import File', ondelete="cascade", index=True,
                                     required=True, auto_join=True)
    sheet_id = fields.Many2one('slm.import.file.sheet', string='Sheet', ondelete="cascade", index=True,
                               required=True, auto_join=True)
    number = fields.Integer('Row number')
    amount = fields.Float('Amount in USD')
    vestcd = fields.Integer('VESTCD')
    dagb = fields.Integer('DAGB')
    stuknr = fields.Char('STUKNR')
    regnr = fields.Char('REGNR')
    boekjr = fields.Integer('BOEKJR')
    per = fields.Integer('PER')
    dag = fields.Integer('DAG')
    mnd = fields.Integer('MND')
    jaar = fields.Integer('JAAR')
    grootb = fields.Char('GROOTB')
    kstnpl = fields.Char('KSTNPL')
    faktnr = fields.Char('FAKTNR')
    pnr = fields.Char('PNR')
    omschr = fields.Char('OMSCHR')
    controle = fields.Char('CONTROLE')
    curcd = fields.Integer('CURCD')
    bedrag = fields.Float('BEDRAG')
    bedrsrd = fields.Float('BEDRSRD')
    bedrusd = fields.Float('BEDRUSD')
    opercde = fields.Integer('OPERCDE')
    vlnr = fields.Char('VLNR')
    gallon = fields.Float('GALLON')
    plcde = fields.Char('PLCDE')
    handl = fields.Char('HANDL')
    maalt = fields.Char('MAALT')
    pax = fields.Integer('PAX')
    mandgn = fields.Integer('MANDGN')
    sdatum = fields.Integer('SDATUM')
    kstnpl6 = fields.Char('KSTNPL6')
    kstnpl7 = fields.Char('KSTNPL7')
    persnr = fields.Integer('PERSNR')
    ponr = fields.Integer('PONR')
    galprijs = fields.Float('GALPRIJS')
    betrekdg = fields.Integer('BETREKDG')
    betrekmd = fields.Integer('BETREKMD')
    betrekjr = fields.Integer('BETREKJR')
    factdg = fields.Integer('FACTDG')
    factmd = fields.Integer('FACTMD')
    factjr = fields.Integer('FACTJR')
    vltype = fields.Char('VLTYPE')
    vltreg = fields.Char('VLTREG')
    cred = fields.Char('CRED')
    deb = fields.Char('DEB')

    def name_get(self):
        return [(record.id, record.number) for record in self]


class ImportFileCategory(models.Model):
    _name = 'slm.import.file.category'

    name = fields.Char('Category name', required=True)


class ImportFileSheet(models.Model):
    _name = 'slm.import.file.sheet'

    import_file_id = fields.Many2one('slm.import.file', string='Import File', ondelete="cascade", index=True,
                                     required=True, auto_join=True)
    name = fields.Char('Name', required=True)
    rows = fields.Integer('Rows')
    balance = fields.Float('Balance')
    credit = fields.Float('Credit')
    debit = fields.Float('Debit')


class ImportFileError(models.Model):
    _name = 'slm.import.file.error'

    import_file_id = fields.Many2one('slm.import.file', string='Import File', ondelete="cascade", index=True,
                                     required=True, auto_join=True)
    sheet_id = fields.Many2one('slm.import.file.sheet', string='Sheet', ondelete="cascade", index=True,
                               required=True, auto_join=True)
    row_id = fields.Many2one('slm.import.file.row', string='Row', ondelete="cascade", index=True,
                             required=True, auto_join=True)
    row_number = fields.Integer('Row number', store=True, related='row_id.number')
    account = fields.Char("Account don't exist")
    vlnr_required = fields.Boolean("Flight number required", default=False)
    analytic_account_required = fields.Char('Analytic account required')
    mandatory_rule = fields.Many2one('account.analytic.mandatory', string='Mandatory rule', ondelete="cascade",
                                     index=True, required=False, auto_join=True)
    curcd_missing = fields.Char("CURCD error")
    missing_creditor = fields.Char("Missing creditor")
    missing_debtor = fields.Char("Missing debtor")
