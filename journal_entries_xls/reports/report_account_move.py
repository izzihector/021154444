from odoo import models, api
from typing import Optional
from xlsxwriter.worksheet import Worksheet, cell_number_tuple, cell_string_tuple


class ReportAccountMoveXLS(models.AbstractModel):
    _name = 'report.account.move.xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, account_moves):
        for obj in account_moves:
            rep = self.env['ir.actions.report'].sudo()._get_report_from_name('account.move.xls')
            report_name = obj.name
            rep.report_file = report_name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            header = workbook.add_format({'bold': True, 'font_size': 20})
            subheader = workbook.add_format({'bold': True, 'font_size': 17})
            column_label = workbook.add_format({'bold': True, 'font_size': 14})
            bold = workbook.add_format({'bold': True})
            date = workbook.add_format({'num_format': 'mm/dd/yy'})
            bold_number = workbook.add_format({'num_format': '[$$-409]#,##0.00;-[$$-409]#,##0.00', 'bold': True})
            number = workbook.add_format({'num_format': '[$$-409]#,##0.00;-[$$-409]#,##0.00'})
            default_format = workbook.add_format({})
            row = 1
            column = 0
            row += 1
            sheet.set_row(row-1, 21)
            sheet.merge_range('A{0}:E{0}'.format(row), obj.name, header)
            row += 2
            sheet.set_row(row-1, 16)
            sheet.write(row, column, 'Date', bold)
            sheet.write(row, column+1, obj.date, date)
            sheet.write(row, column + 5, 'Journal', bold)
            sheet.write(row, column + 6, obj.journal_id.name_get()[0][1] if obj.journal_id else None)
            row += 1
            sheet.set_row(row-1, 16)
            sheet.write(row, column, 'Reference', bold)
            sheet.write(row, column+1, obj.ref, date)
            sheet.write(row, column + 5, 'Branch', bold)
            sheet.write(row, column + 6, obj.branch_id.name if obj.branch_id and obj.branch_id.name else None)
            row += 1
            sheet.set_row(row-1, 16)
            sheet.write(row, column + 5, 'Company', bold)
            sheet.write(row, column + 6, obj.company_id.name)

            row += 3
            sheet.set_row(row, 20)
            sheet.merge_range('A{0}:Z{0}'.format(row+1), 'Journal Items', subheader)

            row += 2
            line_fields = ['account_id', 'partner_id', 'branch_id', 'name', 'analytic_account_id', 'analytic_tag_ids',
                           'amount_currency', 'currency_id', 'debit', 'credit', 'tax_ids', 'pnr', 'faktnr', 'omschr',
                           'controlle', 'bedrsrd', 'bedrsrd', 'opercde', 'regnr', 'vlnr', 'gallon', 'plcde', 'handl',
                           'maalt', 'pax', 'mandgn', 'sdatum', 'kstnpl6', 'kstnpl7', 'persnr', 'ponr', 'galprijs',
                           'betrekdg', 'betrekmd', 'betrekjr', 'factdg', 'factjr', 'vltype', 'vltreg']
            # get all fields
            # line_fields = [field for field in obj.line_ids._fields]
            debit_column = None
            credit_column = None
            row_start = row+1
            row_end = None
            sheet.set_row(row - 1, 19)
            for i, field in enumerate(line_fields):
                sheet.write(row, i, obj.line_ids._fields[field].string, column_label)

            for line in obj.line_ids:
                row += 1
                row_end = row
                for i, field in enumerate(line_fields):
                    current_format = default_format
                    if field == 'debit':
                        debit_column = i
                        current_format = number
                    if field == 'credit':
                        credit_column = i
                        current_format = number
                    try:
                        value = getattr(line, field).name_get()
                        if value:
                            value = value[0][1]
                        else:
                            value = getattr(line, field).name

                    except AttributeError:
                        value = getattr(line, field)
                    sheet.write(row, column + i, value if value != False else None, current_format)

            if debit_column or credit_column:
                row += 1
            if debit_column:
                sheet.write(row, debit_column, '=SUM({0}{1}:{0}{2})'.format(self.colnum_string(debit_column+1),
                                                                            row_start+1, row_end+1), bold_number)
            if credit_column:
                sheet.write(row, credit_column, '=SUM({0}{1}:{0}{2})'.format(self.colnum_string(credit_column+1),
                                                                            row_start+1, row_end+1), bold_number)

            for i in range(0, len(line_fields)):
                self.set_column_auto_width(sheet, i)

    def colnum_string(self, n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string

    def get_column_width(self, worksheet, column):
        """Get the max column width in a `Worksheet` column."""
        strings = getattr(worksheet, '_ts_all_strings', None)
        if strings is None:
            strings = worksheet._ts_all_strings = sorted(
                worksheet.str_table.string_table,
                key=worksheet.str_table.string_table.__getitem__)
        lengths = set()
        for row_id, colums_dict in worksheet.table.items():  # type: int, dict
            data = colums_dict.get(column)
            if not data:
                continue
            if type(data) is cell_string_tuple:
                try:
                    iter_length = len(strings[data.string])
                except IndexError:
                    continue
                if not iter_length:
                    continue
                lengths.add(iter_length)
                continue
            if type(data) is cell_number_tuple:
                iter_length = len(str(data.number))
                if not iter_length:
                    continue
                lengths.add(iter_length)
        if not lengths:
            return None
        return max(lengths)

    def set_column_auto_width(self, worksheet, column):
        """
        Set the width automatically on a column in the `Worksheet`.
        !!! Make sure you run this function AFTER having all cells filled in
        the worksheet!
        """
        max_width = self.get_column_width(worksheet=worksheet, column=column)
        if max_width is None:
            return
        worksheet.set_column(column, column, max_width+2)
