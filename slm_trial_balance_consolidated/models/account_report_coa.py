# -*- coding: utf-8 -*-


from odoo import models, api, _, fields


class report_account_coa(models.AbstractModel):
    _inherit = "account.coa.report"

    # def _get_templates(self):
    #     templates = super(report_account_coa, self)._get_templates()
    #     templates['main_table_header_template'] = 'slm_trial_balance_consolidated.template_coa_table_header'
    #     return templates

    @api.model
    def _get_columns(self, options):
        header1 = [
            {'name': '', 'style': 'width: 100%'},
            {'name': _('Initial Balance'), 'class': 'number', 'colspan': 2},
        ] + [
            {'name': period['string'], 'class': 'number', 'colspan': 2}
            for period in reversed(options['comparison'].get('periods', []))
        ] + [
            {'name': options['date']['string'], 'class': 'number', 'colspan': 2},
            {'name': _('End Balance'), 'class': 'number', 'colspan': 2},
            {'name': _('Profit & Loss'), 'class': 'number', 'colspan': 2},
        ]
        header2 = [
            {'name': '', 'style': 'width:40%'},
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
        ]
        if options.get('comparison') and options['comparison'].get('periods'):
            header2 += [
                {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
                {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
            ] * len(options['comparison']['periods'])
        header2 += [
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
        ]
        return [header1, header2]

    def _post_process(self, grouped_accounts, initial_balances, options, comparison_table):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        title_index = ''
        sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
        zero_value = ''
        sum_columns = [0, 0, 0, 0, 0, 0, 0, 0]
        for period in range(len(comparison_table)):
            sum_columns += [0, 0]
        for account in sorted_accounts:
            # skip accounts with all periods = 0 and no initial balance
            non_zero = False
            for p in range(len(comparison_table)):
                if (grouped_accounts[account][p]['debit'] or grouped_accounts[account][p]['credit']) or\
                        not company_id.currency_id.is_zero(initial_balances.get(account, 0)):
                    non_zero = True
            if not non_zero:
                continue

            initial_balance = initial_balances.get(account, 0.0)
            sum_columns[0] += initial_balance if initial_balance > 0 else 0
            sum_columns[1] += -initial_balance if initial_balance < 0 else 0
            cols = [
                {'name': initial_balance > 0 and self.format_value(
                    initial_balance) or zero_value, 'no_format_name': initial_balance > 0 and initial_balance or 0},
                {'name': initial_balance < 0 and self.format_value(
                    -initial_balance) or zero_value, 'no_format_name': initial_balance < 0 and abs(initial_balance) or 0},
            ]
            total_periods = 0
            for period in range(len(comparison_table)):
                amount = grouped_accounts[account][period]['balance']
                debit = grouped_accounts[account][period]['debit']
                credit = grouped_accounts[account][period]['credit']
                total_periods += amount
                cols += [{'name': debit > 0 and self.format_value(debit) or zero_value, 'no_format_name': debit > 0 and debit or 0},
                         {'name': credit > 0 and self.format_value(credit) or zero_value, 'no_format_name': credit > 0 and abs(credit) or 0}]
                # In sum_columns, the first 2 elements are the initial balance's Debit and Credit
                # index of the credit of previous column generally is:
                p_indice = period * 2 + 1
                sum_columns[(p_indice) + 1] += debit if debit > 0 else 0
                sum_columns[(p_indice) + 2] += credit if credit > 0 else 0

            total_amount = initial_balance + total_periods
            sum_columns[-6] += total_amount if total_amount > 0 else 0
            sum_columns[-5] += -total_amount if total_amount < 0 else 0
            cols += [
                {'name': total_amount > 0 and self.format_value(
                    total_amount) or zero_value, 'no_format_name': total_amount > 0 and total_amount or 0},
                {'name': total_amount < 0 and self.format_value(
                    -total_amount) or zero_value, 'no_format_name': total_amount < 0 and abs(total_amount) or 0},
            ]
            if int(account.code[0]) >= 4 and account.code != '999999':
                cols += [{'name': zero_value, 'no_format_name': zero_value},
                         {'name': zero_value, 'no_format_name': zero_value}]
                sum_columns[-2] += total_amount if total_amount > 0 else 0
                sum_columns[-1] += -total_amount if total_amount < 0 else 0
            else:
                sum_columns[-4] += total_amount if total_amount > 0 else 0
                sum_columns[-3] += -total_amount if total_amount < 0 else 0
            cols += [
                {'name': total_amount > 0 and self.format_value(
                    total_amount) or zero_value, 'no_format_name': total_amount > 0 and total_amount or 0},
                {'name': total_amount < 0 and self.format_value(
                    -total_amount) or zero_value, 'no_format_name': total_amount < 0 and abs(total_amount) or 0},
            ]
            name = account.code + " " + account.name
            lines.append({
                'id': account.id,
                'name': len(name) > 40 and not context.get('print_mode') and name[:40]+'...' or name,
                'title_hover': name,
                'columns': cols,
                'unfoldable': False,
                'caret_options': 'account.account',
            })

        lines.append({
            'id': 'grouped_accounts_total',
            'name': _('Total'),
            'class': 'total',
            'columns': [{'name': self.format_value(v)} for v in sum_columns],
            'level': 1,
        })

        difference_columns = [{'name': zero_value}] * len(sum_columns)
        difference_columns[-2] = {'name': self.format_value(
            sum_columns[-2] - sum_columns[-1])}
        difference_columns[-4] = {'name': self.format_value(
            sum_columns[-4] - sum_columns[-3])}

        lines.append({
            'id': 'difference_total',
            'name': '',
            'class': 'difference',
            'columns': difference_columns,
        })
        return lines

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
            for i, value in enumerate(sums):
                # Update totals.
                totals[i] += value

                # Create columns.
                columns.append({'name': self.format_value(value, blank_if_zero=True), 'class': 'number', 'no_format_name': value})

            name = account.name_get()[0][1]

            lines.append({
                'id': self._get_generic_line_id('account.account', account.id),
                'name': name,
                'title_hover': name,
                'columns': columns,
                'unfoldable': False,
                'caret_options': 'account.account',
                'class': 'o_account_searchable_line o_account_coa_column_contrast',
            })

        # Total report line.
        lines.append({
             'id': self._get_generic_line_id(None, None, markup='grouped_accounts_total'),
             'name': _('Total'),
             'class': 'total o_account_coa_column_contrast',
             'columns': [{'name': self.format_value(total), 'class': 'number'} for total in totals],
             'level': 1,
        })

        return lines
