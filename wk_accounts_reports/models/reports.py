from copy import deepcopy
import io
import base64
from io import BytesIO
from odoo.tools.misc import xlsxwriter
import odoo 
from odoo.tools.mimetypes import guess_mimetype
from odoo import models, api, _
import logging
_logger = logging.getLogger(__name__)

class AccountChartOfAccountReport(models.AbstractModel):
    _inherit = "account.coa.report"

    filter_partner = True
    filter_movements = True

    @api.model
    def _get_columns(self, options):
        headers = super()._get_columns(options)
        if self.env.context and  self.env.context.get('print_mode'):
            headers[0].insert(1,{'name': '', 'style': 'width:20%'},)
            headers[1].insert(1,{'name': '', 'style': 'width:20%'},)
        return headers

    @api.model
    def _get_lines(self, options, line_id=None):
        # Create new options with 'unfold_all' to compute the initial balances.
        # Then, the '_do_query' will compute all sums/unaffected earnings/initial balances for all comparisons.
        new_options = options.copy()
        new_options['unfold_all'] = True
        options_list = self._get_options_periods_list(new_options)
        accounts_results, taxes_results = self.env['account.general.ledger']._do_query(options_list, fetch_lines=False)

        lines = []
        totals = [0.0] * (2 * (len(options_list) + 2))
        # Add lines, one per account.account record.
        for account, periods_results in accounts_results:
            sums = []
            account_balance = 0.0
            for i, period_values in enumerate(reversed(periods_results)):
                account_sum = period_values.get('sum', {})
                account_un_earn = period_values.get('unaffected_earnings', {})
                account_init_bal = period_values.get('initial_balance', {})

                if i == 0:
                    # Append the initial balances.
                    initial_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
                    sums += [
                        initial_balance > 0 and initial_balance or 0.0,
                        initial_balance < 0 and -initial_balance or 0.0,
                    ]
                    account_balance += initial_balance

                # Append the debit/credit columns.
                sums += [
                    account_sum.get('debit', 0.0) - account_init_bal.get('debit', 0.0),
                    account_sum.get('credit', 0.0) - account_init_bal.get('credit', 0.0),
                ]
                account_balance += sums[-2] - sums[-1]

            # Append the totals.
            sums += [
                account_balance > 0 and account_balance or 0.0,
                account_balance < 0 and -account_balance or 0.0,
            ]

            # account.account report line.
            columns = []
            movements = False
            if options.get('movements'):
                movements = all(x==0 for x in sums)
            if options.get('movements'):
                if not movements: 
                    for i, value in enumerate(sums):
                        # Update totals.
                        totals[i] += value

                        # Create columns.
                        columns.append({'name': self.format_value(value, blank_if_zero=True), 'class': 'number', 'no_format_name': value})
            else:
                for i, value in enumerate(sums):
                    # Update totals.
                    totals[i] += value

                    # Create columns.
                    columns.append({'name': self.format_value(value, blank_if_zero=True), 'class': 'number', 'no_format_name': value})
            
            name = account.name_get()[0][1]
            if options.get('movements'):
                if not movements:
                    lines.append({
                        'id': account.id,
                        'name': account.code if self.env.context and self.env.context.get('print_mode') else name,
                        'title':account.name,
                        'title_hover': name,
                        'columns': columns,
                        'unfoldable': False,
                        'caret_options': 'account.account',
                        'class': 'o_account_searchable_line o_account_coa_column_contrast',
                    })
            else:
                lines.append({
                        'id': account.id,
                        'name': account.code if self.env.context and self.env.context.get('print_mode') else name ,
                        'title':account.name,
                        'title_hover': name,
                        'columns': columns,
                        'unfoldable': False,
                        'caret_options': 'account.account',
                        'class': 'o_account_searchable_line o_account_coa_column_contrast',
                    })
        columns_lst = [{'name': '' }] if self.env.context and self.env.context.get('print_mode') else []
        lines.append({
             'id': 'grouped_accounts_total',
             'name': _('Total'),
             'class': 'total o_account_coa_column_contrast',
             'columns': columns_lst +[{'name': self.format_value(total), 'class': 'number'} for total in totals],
             'level': 1,
        })
        return lines

    def get_xlsx(self, options, response=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'strings_to_formulas': False,
        })
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})

        #Set the first column width to 50
        sheet.set_column(0, 0, 50)

        y_offset = 0
        if self.env.company and self.env.company.logo:
            sheet.set_row(y_offset,20)
            mimetype = guess_mimetype(base64.b64decode(self.env.company.logo))
            if (mimetype.startswith('image')):
                img_format = mimetype.split('/')[1]
                cell_value = odoo.tools.image_process(base64_source=self.env.company.logo, size=(150 or None, 150 or None),crop=False, quality=0)
                imgdata = base64.b64decode(cell_value)
                image = BytesIO(imgdata)
                sheet.insert_image(y_offset , 0, "image.{}".format(img_format), {'image_data': image, 'positioning': 1, 'x_scale': 0.8, 'y_scale': 0.8})
            y_offset += 1

        headers, lines = self.with_context(no_format=True, print_mode=True, prefetch_fields=False)._get_table(options)

        # Add headers.
        for header in headers:
            x_offset = 0
            for column in header:
                column_name_formated = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
                colspan = column.get('colspan', 1)
                if colspan == 1:
                    sheet.write(y_offset, x_offset, column_name_formated, title_style)
                else:
                    sheet.merge_range(y_offset, x_offset, y_offset, x_offset + colspan - 1, column_name_formated, title_style)
                x_offset += colspan
            y_offset += 1

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)
        # Add lines.
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style
            cell = 0
            #write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, cell, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, cell, cell_value, col1_style)
            if lines[y].get('id') != 'grouped_accounts_total':
                cell +=1
                cell_type, cell_value = self._get_cell_code_value(lines[y])
                sheet.write(y + y_offset, cell, cell_value, col1_style)
            cell += 1
            #write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                # if x
                cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, cell + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    sheet.write(y + y_offset, cell + lines[y].get('colspan', 1) - 1, cell_value, style)
                cell+=1
        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return generated_file

    def _get_cell_code_value(self, cell):
            # the date is not parsable thus is returned as text
            if cell.get('title'):
                return ('text', cell['title'])
            else:
                return ('text', '')

    @api.model
    def _get_options_domain(self, options):
        domain = super()._get_options_domain(options)
        domain += self._get_options_movements(options)
        return domain

    @api.model
    def _get_options_movements(self, options):
        if options.get('movements'):
            return ['|',('credit', '<>', 0),('debit','<>',0)]
        return [('credit', '=', 0),('debit','=',0)]

class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"

    filter_partner = True
