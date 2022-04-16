# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, exceptions, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _run_create_invoice_edgar(self):
        self.create_invoice_edgar()

    def create_invoice_edgar(self):
        cr = self.env.cr
        invoice_obj = self.env['account.move']
        inv = {}
        inv_line = []
        item = 0
        try:
            query = (
                '''select se.pnrr as pnr from slm_edgard se where se.sheet_name = 'SALES JOURN' group by pnr;''')
            cr.execute(query, [])
            for pnr in cr.dictfetchall():
                inv_line = []
                sql = ('''select se.id as id, se.company_id as company_id, se.branch_code as branch_code, se.day_book as day_book, se.piece_number as piece_number,\
                            se.registration_number as registration_number, se.book_year as book_year, se.period as period, se.account_number as account_number,\
                            se.cost_center as cost_center, se.invoice_number as invoice_number, se.description as description, se.currency_code as currency_code,\
                            se.amount as amount, se.amount_srd as amount_srd, se.amount_usd as amount_usd, se.operation_code, se.date as date, se.date_read as date_read,\
                            se.ticketnumber as ticketnumber, se.row_count as row_count, se.pnrr as pnr\
                            from slm_edgard se\
                            where se.sheet_name = 'SALES JOURN' and se.pnrr = %s;''')
                cr.execute(sql, [pnr['pnr']])
                for row in cr.dictfetchall():
                    item += 1
                    line = self.create_invoice_line_edgar(row)
                    inv_line.append((0, 0, line))
                    inv = {
                        'partner_id': 2682,
                        'number': row.get('pnr', ""),
                        'move_name': row.get('pnr', ""),
                        'date_invoice': datetime.strptime(str(row['date']), '%Y-%m-%d %H:%M:%S').date(),
                        'journal_id': 20,
                        # 'branch_id': self.get_branch(row['branch_code']) or False,
                        'company_id': 2,
                        'account_id': 744,
                        'piece_number': row.get('piece_number', ""),
                        'reference': row.get('ticketnumber', ""),
                        'book_year': row.get('book_year', ""),
                        'period': row.get('period', ""),
                        'type': 'out_invoice',
                        'state': 'draft',
                        'invoice_line_ids': inv_line,
                    }
                invoice_obj.create(inv)
                # if item == 1:
                cr.commit()
        except Exception as e:
            print(e)
            cr.rollback()
            pass

    def create_move_margo_old(self):
        cr = self.env.cr
        move_obj = self.env['account.move']
        move = {}
        move_lines = []
        num_line = 0
        log_file = "Journal Entries Log" + "\n"
        try:
            sql = ('''select sm.sheet_name as sheet_name \
                        from slm_edgard sm \
                        where sm.sheet_name != 'SALES JOURN' \
                        group by sm.sheet_name;''')
            cr.execute(sql, [])
            for row in cr.dictfetchall():
                move_lines = self.get_move_lines(row)
                if move_lines:
                    num_line += 1
                    move = {
                        'journal_id': 20,
                        'date': datetime.strptime(str(move_lines[2]), '%Y-%m-%d %H:%M:%S').date(),
                        'company_id': 2,
                        'ref': "%s %s" % (row['sheet_name'], datetime.strptime(str(move_lines[2]), '%Y-%m-%d %H:%M:%S').date()),
                        'line_ids': move_lines[0],
                    }
                    try:
                        # Log Data import --> Successful
                        log_file += "Line : %s Sheet name: %s -> Successful" % (
                            num_line, row['sheet_name'])
                        log_file += "\n"
                        log_file += move_lines[5]
                        log_file += "\n"
                        log_file += "Debe: %s Haber: %s Debe USD: %s Haber USD: %s" % (
                            move_lines[6], move_lines[8], move_lines[7], move_lines[9])
                        log_file += "\n"
                        move_obj.create(move)
                        cr.commit()
                    except exceptions as ex:
                        # Log data Import --> Errors
                        log_file += "Line : %s Sheet name: %s Error: %s " % (
                            num_line, row['sheet_name'], ex)
                        log_file += "\n"
                        log_file += move_lines[5]
                        log_file += "\n"
                        log_file += "Debe: %s Haber: %s Debe USD: %s Haber USD: %s" % (
                            move_lines[6], move_lines[7], move_lines[8], move_lines[9])
                        log_file += "\n"
                        cr.rollback()
                        pass
        except Exception as e:
            print(e)
            log_file += "Line : %s Error: %s " % (num_line, e)
            log_file += "\n"
            cr.rollback()
            pass
        finally:
            return log_file

    def create_move_margo(self):
        cr = self.env.cr
        move_obj = self.env['account.move']
        move = {}
        move_lines = []
        num_line = 0
        log_file = "Journal Entries Log" + "\n"
        # try:
        sql = ('''select sm.sheet_name as sheet_name \
                    from slm_edgard sm \
                    where sm.sheet_name != 'SALES JOURN' \
                    group by sm.sheet_name;''')
        cr.execute(sql, [])
        for row in cr.dictfetchall():
            move_lines = self.get_move_lines(row)
            if 'warning' in move_lines:
                return move_lines
            if move_lines:
                num_line += 1
                move = {
                    'journal_id': 20,
                    'date': datetime.strptime(str(move_lines[2]), '%Y-%m-%d %H:%M:%S').date(),
                    'company_id': 2,
                    'ref': "%s %s" % (row['sheet_name'], datetime.strptime(str(move_lines[2]), '%Y-%m-%d %H:%M:%S').date()),
                    'line_ids': move_lines[0],
                }
                log_file += "Line : %s Sheet name: %s -> Successful" % (
                    num_line, row['sheet_name'])
                log_file += "\n"
                log_file += move_lines[5]
                log_file += "\n"
                log_file += "Debe: %s Haber: %s Debe USD: %s Haber USD: %s" % (
                    move_lines[6], move_lines[8], move_lines[7], move_lines[9])
                log_file += "\n"
                move_obj.create(move)
                cr.commit()
                log_file += "Debe: %s Haber: %s Debe USD: %s Haber USD: %s" % (
                    move_lines[6], move_lines[7], move_lines[8], move_lines[9])
                log_file += "\n"
        return log_file

    def get_move_lines_old(self, row):
        cr = self.env.cr
        lines = []
        line = {}
        date = False
        day_book = False
        debit = 0.00
        credit = 0.00
        sum_debe = 0.00
        sum_debe_usd = 0.00
        sum_haber = 0.00
        sum_haber_usd = 0.00
        log_line = ""
        num_line = 0
        try:
            if row:
                sql = ('''select se.id as id , se.company_id as company_id, se.branch_code as branch_code, se.day_book as day_book, se.piece_number as piece_number,\
                            se.registration_number as registration_number, se.book_year as book_year, se.period as period, se.account_number as account_number,\
                            se.cost_center as cost_center, se.invoice_number as invoice_number, se.description as description, se.currency_code as currency_code,\
                            COALESCE(round(se.amount::numeric,2),0.00) as amount, COALESCE(round(se.amount_srd::numeric,2),0.00) as amount_srd, COALESCE(round(se.amount_usd::numeric,2), 0.00) as amount_usd, se.operation_code as operation_code, se.date as date,\
                            se.date_read as date_read, se.row_count as row_count, se.flight_number as flight_number, se.place_code as place_code, se.handling as handling, se.passengers as passengers, se.man_days as man_days, se.s_date as s_date, se.cost_center_6 as cost_center_6, se.cost_center_7 as cost_center_7, se.personne as personne,\
                            se.purchase as purchase, se.gallon_pr as gallon_pr, se.current_day as current_day, se.current_month as current_month, se.current_year as current_year, se.invoice_day as invoice_day, se.invoice_month as invoice_month, se.invoice_year as invoice_year, se.air_plane_type as air_plane_type, se.creditors as creditors, se.debtors as debitors\
                            from slm_edgard se\
                            where se.sheet_name = %s;''')
                cr.execute(sql, [row['sheet_name']])
                for l in cr.dictfetchall():
                    amount_usd = 0.00
                    amount = 0.00
                    num_line += 1
                    day_book = l['day_book']
                    date = l['date']
                    amounts = self.get_amount(l.get('currency_code', ''), l.get('amount', 0.00), l.get(
                        'amount_srd', 0.00), l.get('amount_usd', 0.00),  datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S').date())
                    try:
                        currency_id = amounts[0]
                    except TypeError:
                        currency_id = 2
                    try:
                        amount = amounts[1]
                    except TypeError:
                        amount = l.get('amount', 0.00)
                    try:
                        amount_usd = amounts[2]
                    except TypeError:
                        amount_usd = l.get('amount_usd', 0.00)
                    account_id = self.get_account(
                        l['account_number'], l['branch_code'])
                    if not account_id:
                        # return {'warning': 'Row no {} - Account {} not found'.format(num_line, l['account_number'])}
                        log_line += 'Row no {} - Account {} not found'.format(
                            num_line, l['account_number'])
                        log_line += "\n"
                        pass
                    if l['amount'] >= 0.00:
                        debit += l['amount']
                        sum_debe += round(amount, 6)
                        sum_debe_usd += round(amount_usd, 6)
                        line = {
                            'account_id': account_id,
                            # 'account_id': self.get_account(l['account_number'], l['branch_code']),
                            'name': l['description'] or "",
                            # 'branch_id': self.get_branch(l['branch_code']) or False,
                            'analytic_account_id': self.get_analytic_account(l['cost_center']),
                            'currency_id': currency_id or False,
                            'amount_currency': round(amount, 6) or 0.00,
                            'debit': round(amount_usd, 6) or 0.00,
                            'credit': 0.00,
                            'bedrsrd': float(l.get('amount_srd', 0.00)) or 0.00,
                            'bedrusd': float(l.get('amount_usd', 0.00)) or 0.00,
                            'faktnr': str(l.get('invoice_number', False)) or False,
                            'omschr': str(l.get('description', False)) or False,
                            'vlnr': self.get_flight_number(l.get('flight_number')),
                            # 'vlnr': str(l.get('flight_number', False)) or False,
                            'plcde': str(l.get('place_code', False)) or False,
                            'handl': str(l.get('handling', False)) or False,
                            'pax': str(l.get('passengers', False)) or False,
                            'mandgn': str(l.get('man_days', False)) or False,
                            'kstnpl6': str(l.get('cost_center_6', False)) or False,
                            'kstnpl7': str(l.get('cost_center_7', False)) or False,
                            'persnr': str(l.get('personne', False)) or False,
                            'ponr': str(l.get('purchase', False)) or False,
                            'galprijs': str(l.get('gallon_pr', False)) or False,
                            'betrekdg': str(l.get('current_day', False)) or False,
                            'betrekmd': str(l.get('current_month', False)) or False,
                            'betrekjr': str(l.get('current_year', False)) or False,
                            'factdg': str(l.get('invoice_day', False)) or False,
                            'factmd': str(l.get('invoice_month', False)) or False,
                            'factjr': str(l.get('invoice_year', False)) or False,
                            'vltype': str(l.get('air_plane_type', False)) or False,
                            'vltreg': str(l.get('air_plane_registration', False)) or False,
                            'opercde': str(l.get('operation_code', False)) or False,
                            'regnr': str(l.get('registration_number', False)) or False,
                            'pnr': str(l.get('pnrr', False)) or False,
                        }
                        log_line += str(line) + "\n"
                    elif l['amount'] < 0.00:
                        credit += l['amount']
                        sum_haber += round(amount, 6)
                        sum_haber_usd += round(amount_usd, 6)
                        account_id = self.get_account(
                            l['account_number'], l['branch_code'])
                        line = {
                            'account_id': account_id,
                            # 'account_id': self.get_account(l['account_number'], l['branch_code']),
                            'name': l['description'] or "",
                            # 'branch_id': self.get_branch(l['branch_code']) or False,
                            'analytic_account_id': self.get_analytic_account(l['cost_center']),
                            'currency_id': currency_id or False,
                            'amount_currency':  round(amount, 6) or 0.00,
                            'debit': 0.00,
                            'credit': abs(round(amount_usd, 6)) or 0.00,
                            'bedrsrd': float(l.get('amount_srd', 0.00)) or 0.00,
                            'bedrusd': float(l.get('amount_usd', 0.00)) or 0.00,
                            'faktnr': str(l.get('invoice_number', False)) or False,
                            'omschr': str(l.get('description', False)) or False,
                            'vlnr': self.get_flight_number(l.get('flight_number')),
                            # 'vlnr': str(l.get('flight_number', False)) or False,
                            'plcde': str(l.get('place_code', False)) or False,
                            'handl': str(l.get('handling', False)) or False,
                            'pax': str(l.get('passengers', False)) or False,
                            'mandgn': str(l.get('man_days', False)) or False,
                            'kstnpl6': str(l.get('cost_center_6', False)) or False,
                            'kstnpl7': str(l.get('cost_center_7', False)) or False,
                            'persnr': str(l.get('personne', False)) or False,
                            'ponr': str(l.get('purchase', False)) or False,
                            'galprijs': str(l.get('gallon_pr', False)) or False,
                            'betrekdg': str(l.get('current_day', False)) or False,
                            'betrekmd': str(l.get('current_month', False)) or False,
                            'betrekjr': str(l.get('current_year', False)) or False,
                            'factdg': str(l.get('invoice_day', False)) or False,
                            'factmd': str(l.get('invoice_month', False)) or False,
                            'factjr': str(l.get('invoice_year', False)) or False,
                            'vltype': str(l.get('air_plane_type', False)) or False,
                            'vltreg': str(l.get('air_plane_registration', False)) or False,
                            'opercde': str(l.get('operation_code', False)) or False,
                            'regnr': str(l.get('registration_number', False)) or False,
                            'pnr': str(l.get('pnrr', False)) or False,
                        }
                        log_line += str(line) + "\n"
                    lines.append((0, 0, line))
        except Exception as e:
            # print(e)
            log_line += "Line : %s Error: %s " % (num_line, e)
            log_line += "\n"
            pass
        finally:
            return lines, day_book, date, debit, credit, log_line, sum_debe, sum_debe_usd, sum_haber, sum_haber_usd

    def get_move_lines(self, row):
        cr = self.env.cr
        lines = []
        line = {}
        date = False
        day_book = False
        debit = 0.00
        credit = 0.00
        sum_debe = 0.00
        sum_debe_usd = 0.00
        sum_haber = 0.00
        sum_haber_usd = 0.00
        log_line = ""
        num_line = 0
        # try:
        if row:
            sql = ('''select se.id as id , se.company_id as company_id, se.branch_code as branch_code, se.day_book as day_book, se.piece_number as piece_number,\
                        se.registration_number as registration_number, se.book_year as book_year, se.period as period, se.account_number as account_number,\
                        se.cost_center as cost_center, se.invoice_number as invoice_number, se.description as description, se.currency_code as currency_code,\
                        COALESCE(round(se.amount::numeric,2),0.00) as amount, COALESCE(round(se.amount_srd::numeric,2),0.00) as amount_srd, COALESCE(round(se.amount_usd::numeric,2), 0.00) as amount_usd, se.operation_code as operation_code, se.date as date,\
                        se.date_read as date_read, se.row_count as row_count, se.flight_number as flight_number, se.place_code as place_code, se.handling as handling, se.passengers as passengers, se.man_days as man_days, se.s_date as s_date, se.cost_center_6 as cost_center_6, se.cost_center_7 as cost_center_7, se.personne as personne,\
                        se.purchase as purchase, se.gallon_pr as gallon_pr, se.current_day as current_day, se.current_month as current_month, se.current_year as current_year, se.invoice_day as invoice_day, se.invoice_month as invoice_month, se.invoice_year as invoice_year, se.air_plane_type as air_plane_type, se.creditors as creditors, se.debtors as debitors\
                        from slm_edgard se\
                        where se.sheet_name = %s;''')
            cr.execute(sql, [row['sheet_name']])
            for l in cr.dictfetchall():
                num_line += 1
                day_book = l['day_book']
                date = l['date']
                amounts = self.get_amount(l.get('currency_code', ''), l.get('amount', 0.00), l.get(
                    'amount_srd', 0.00), l.get('amount_usd', 0.00),  datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S').date())
                try:
                    currency_id = amounts[0]
                except TypeError:
                    currency_id = 2
                try:
                    amount = amounts[1]
                except TypeError:
                    amount = l.get('amount', 0.00)
                try:
                    amount_usd = amounts[2]
                except TypeError:
                    amount_usd = l.get('amount_usd', 0.00)
                account_id = self.get_account(
                    l['account_number'], l['branch_code'])
                if not account_id:
                    return {'warning': 'Row no {} - Account {} not found'.format(num_line, l['account_number'])}

                if l['amount'] > 0.00:
                    debit += l['amount']
                    sum_debe += float(round(amount, 6))
                    sum_debe_usd += float(round(amount_usd, 6))
                    line = {
                        'account_id': account_id,
                        'name': l['description'] or "",
                        # 'branch_id': self.get_branch(l['branch_code']) or False,
                        'analytic_account_id': self.get_analytic_account(l['cost_center']),
                        'currency_id': currency_id or 2,
                        'amount_currency': float(round(amount, 6)) or 0.00,
                        'debit': float(round(amount_usd, 6)) or 0.00,
                        'credit': 0.00,
                        'bedrsrd': float(l.get('amount_srd', 0.00)) or 0.00,
                        'bedrusd': float(l.get('amount_usd', 0.00)) or 0.00,
                        'faktnr': str(l.get('invoice_number', False)) or False,
                        'omschr': str(l.get('description', False)) or False,
                        'vlnr': self.get_flight_number(l.get('flight_number')) or False,
                        'plcde': str(l.get('place_code', False)) or False,
                        'handl': str(l.get('handling', False)) or False,
                        'pax': int(l.get('passengers', 0)) or False,
                        'mandgn': int(l.get('man_days', 0)) or False,
                        'kstnpl6': str(l.get('cost_center_6', False)) or False,
                        'kstnpl7': str(l.get('cost_center_7', False)) or False,
                        'persnr': str(l.get('personne', False)) or False,
                        'ponr': str(l.get('purchase', False)) or False,
                        'galprijs': str(l.get('gallon_pr', False)) or False,
                        'betrekdg': str(l.get('current_day', False)) or False,
                        'betrekmd': str(l.get('current_month', False)) or False,
                        'betrekjr': str(l.get('current_year', False)) or False,
                        'factdg': str(l.get('invoice_day', False)) or False,
                        'factmd': str(l.get('invoice_month', False)) or False,
                        'factjr': str(l.get('invoice_year', False)) or False,
                        'vltype': str(l.get('air_plane_type', False)) or False,
                        'vltreg': str(l.get('air_plane_registration', False)) or False,
                        'opercde': str(l.get('operation_code', False)) or False,
                        'regnr': str(l.get('registration_number', False)) or False,
                    }
                    log_line += str(line) + "\n"
                elif l['amount'] < 0.00:
                    credit += l['amount']
                    sum_haber += float(round(amount, 6))
                    sum_haber_usd += float(round(amount_usd, 6))
                    line = {
                        'account_id': account_id,
                        'name': l['description'] or "",
                        # 'branch_id': self.get_branch(l['branch_code']) or False,
                        'analytic_account_id': self.get_analytic_account(l['cost_center']),
                        'currency_id': currency_id or 2,
                        'amount_currency':  float(round(amount, 6)) or 0.00,
                        'debit': 0.00,
                        'credit': float(abs(round(amount_usd, 6))) or 0.00,
                        'bedrsrd': float(l.get('amount_srd', 0.00)) or 0.00,
                        'bedrusd': float(l.get('amount_usd', 0.00)) or 0.00,
                        'faktnr': str(l.get('invoice_number', False)) or False,
                        'omschr': str(l.get('description', False)) or False,
                        'vlnr': self.get_flight_number(l.get('flight_number')) or False,
                        'plcde': str(l.get('place_code', False)) or False,
                        'handl': str(l.get('handling', False)) or False,
                        'pax': str(l.get('passengers', False)) or False,
                        'mandgn': str(l.get('man_days', False)) or False,
                        'kstnpl6': str(l.get('cost_center_6', False)) or False,
                        'kstnpl7': str(l.get('cost_center_7', False)) or False,
                        'persnr': str(l.get('personne', False)) or False,
                        'ponr': str(l.get('purchase', False)) or False,
                        'galprijs': str(l.get('gallon_pr', False)) or False,
                        'betrekdg': str(l.get('current_day', False)) or False,
                        'betrekmd': str(l.get('current_month', False)) or False,
                        'betrekjr': str(l.get('current_year', False)) or False,
                        'factdg': str(l.get('invoice_day', False)) or False,
                        'factmd': str(l.get('invoice_month', False)) or False,
                        'factjr': str(l.get('invoice_year', False)) or False,
                        'vltype': str(l.get('air_plane_type', False)) or False,
                        'vltreg': str(l.get('air_plane_registration', False)) or False,
                        'opercde': str(l.get('operation_code', False)) or False,
                        'regnr': str(l.get('registration_number', False)) or False,
                    }
                    log_line += str(line) + "\n"
                lines.append((0, 0, line))
        return lines, day_book, date, debit, credit, log_line, sum_debe, sum_debe_usd, sum_haber, sum_haber_usd

    def get_amount(self, currency_code, amount, amount_srd, amount_usd, date_import):
        usd_code = '840'
        if currency_code and amount:
            if amount and amount_usd:
                currency_id = self.get_currency(currency_code)
                return currency_id.id, amount, amount_usd
            else:
                if currency_code == usd_code and not amount_usd:
                    currency_id = self.get_currency(usd_code)
                    return False, 0.00, amount
                elif currency_code == usd_code and amount_usd:
                    currency_id = self.get_currency(usd_code)
                    return False, 0.00, amount_usd
                elif currency_code != usd_code and not amount_usd:
                    currency_id = self.get_currency(currency_code)
                    company_id = self.env['res.company'].search(
                        [('id', '=', 2)], limit=1)
                    amount_usd = currency_id._convert(amount, company_id.currency_id, company_id, str(
                        date_import) or fields.Date.today(), False)
                    return currency_id.id, amount, round(amount_usd, 6)

    def get_currency(self, currency_code):
        currency_obj = self.env['res.currency']
        currency_id = False
        if currency_code:
            currency_id = currency_obj.search(
                [('currency_code', '=', currency_code)], limit=1)
        return currency_id

    def create_invoice_line_edgar(self, row):
        line = {}
        if row:
            line = {
                'name': row['description'] or "",
                'account_id': self.get_account(row['account_number'], row['branch_code']) or False,
                'quantity': 1.00,
                'price_unit': row['amount'],
                'registration_number': row['registration_number'],
                'analytic_account_ids': False,
            }
        return line

    def get_analytic_account(self, analytic_account):
        analytic_obj = self.env['account.analytic.account']
        account_id = False
        if analytic_account:
            account_id = analytic_obj.search(
                [('code', '=', analytic_account)], limit=1)
        return account_id and account_id.id or False

    def get_branch(self, branch_code):
        branch_obj = self.env['res.branch']
        branch_id = False
        if branch_code:
            branch_id = branch_obj.search(
                [('branch_code', '=', branch_code)], limit=1)
        return branch_id.id

    def get_account(self, account_number, branch_code):
        account_obj = self.env['account.account']
        account_id = False
        company_id = False
        if account_number:
            if branch_code:
                company_id = self.env.user.company_id.id
            account_id = account_obj.search(
                [('code', '=', account_number), ('company_id', '=', 2)], limit=1)
        return account_id and account_id.id

    def get_company(self, branch_code):
        branch_obj = self.env['res.branch']
        branch_id = False
        if branch_code:
            branch_id = branch_obj.search(
                [('branch_code', '=', branch_code)], limit=1)
        return branch_id.company_id.id

    def get_journal(self, day_book):
        journal_obj = self.env['account.journal']
        journal_id = False
        if day_book:
            journal_id = journal_obj.search(
                [('day_book', '=', day_book)], limit=1)
        return journal_id.id

    def get_flight_number(self, flight_number_name):
        flight_number_obj = self.env['flight.list']
        if flight_number_name:
            flight_number = flight_number_obj.search(
                [('name', '=', flight_number_name)], limit=1)
            if flight_number:
                return flight_number.id
            else:
                return False


AccountMove()
