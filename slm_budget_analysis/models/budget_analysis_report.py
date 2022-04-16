# -*- coding: utf-8 -*-

import collections
from odoo import models, api, _


class BudgetAnalysisReport(models.AbstractModel):
    _name = "budget.analysis.report"
    _description = "Budget Analysis  Report"
    _inherit = "account.report"

    filter_date = {'date_from': '', 'date_to': '', 'mode': 'range', 'filter': 'this_month'}
    filter_comparison = None
    filter_cash_basis = None
    filter_all_entries = None
    filter_hierarchy = None
    filter_unfold_all = None
    filter_multi_company = None
    filter_profit_center_accounts = None
    filter_encryption = None

    columns = 100

    @api.model
    def _get_report_name(self):
        return _("Budget Analysis Report")

    def _get_templates(self):
        templates = super(BudgetAnalysisReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    def _get_columns_name(self, options):
        columns = self.columns
        return [{'name': ''}] * (columns + 3)

    def _do_query(self, options, line_id):
        context = dict(self._context or {})
        sql_start = """
                SELECT account,
                       account_name,
                       analytic_account,
                       analytic_account_name,
                       tag,
                       sum(budget_balance) AS budget_balance,
                       sum(balance) AS balance
                FROM (
        """
        sql_budget_main = """
            SELECT AA.code                                   AS account,
                   AA.name                                   AS account_name,
                   AAT.name                                  AS tag,
                   AAA.code                                  AS analytic_account,
                   AAA.name                                  AS analytic_account_name,
                   CBL.planned_amount                       AS budget_balance,
                   0                                            AS balance
            FROM crossovered_budget CB
                   JOIN crossovered_budget_lines CBL ON (CB.id = CBL.crossovered_budget_id)
                   JOIN account_budget_post ABP ON (CBL.general_budget_id = ABP.id)
                   JOIN account_budget_rel ABR ON (ABP.id = ABR.budget_id)
                   JOIN account_account AA ON (AA.id = ABR.account_id)
                   JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AA.id)
                   JOIN account_account_tag AAT ON (AAT.id = AAAT.account_account_tag_id)
                   JOIN account_analytic_account AAA ON (AAA.id = CBL.analytic_account_id)
            WHERE CBL.date_from >= %s
              AND CBL.date_to <= %s
        """

        union = """ UNION ALL """

        sql_budget_all = """
                    SELECT DISTINCT
                           AA.code     AS account,
                           AA.name     AS account_name,
                           AAT.name    AS tag,
                           ''          AS analytic_account,
                           ''          AS analytic_account_name,
                           0            AS budget_balance,
                           0           AS balance
                    FROM account_account AA
                           JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AA.id)
                           JOIN account_account_tag AAT ON (AAAT.account_account_tag_id = AAT.id)
                           CROSS JOIN account_analytic_account AAA_BEM
                    WHERE AA.code SIMILAR TO %s
                      AND AA.code != '999999'
                      AND AA.deprecated = FALSE
                """

        sql_balance_main = """
                    SELECT AA.code     AS account,
                           AA.name     AS account_name,
                           AAT.name    AS tag,
                           AAA.code    AS analytic_account,
                           AAA.name    AS analytic_account_name,
                           0                       AS budget_balance,
                           balance
                    FROM account_analytic_account AAA
                             JOIN account_move_line AML ON (AML.analytic_account_id = AAA.id)
                             JOIN account_account AA ON (AML.account_id = AA.id)
                             JOIN account_move AM ON (AM.id = AML.move_id)
                             JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AML.account_id)
                             JOIN account_account_tag AAT ON (AAAT.account_account_tag_id = AAT.id)
                             LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                        AND RCR.name = date_trunc('month', AML.date)::date)
                    WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
                      AND AML.date <= %s
                      AND AML.date >= %s
                      AND AM.state = %s
                      AND AA.code SIMILAR TO %s
                      AND AA.code != '999999'
                """

        sql_balance_all = """
                   SELECT DISTINCT
                          AA.code     AS account,
                          AA.name     AS account_name,
                          AAT.name    AS tag,
                          ''          AS analytic_account,
                          ''          AS analytic_account_name,
                          0           AS balance,
                           0           AS budget_balance
                   FROM account_account AA
                          JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AA.id)
                          JOIN account_account_tag AAT ON (AAAT.account_account_tag_id = AAT.id)
                          CROSS JOIN account_analytic_account AAA_EM
                   WHERE AA.code SIMILAR TO %s
                     AND AA.code != '999999'
                     AND AA.deprecated = FALSE
               """

        sql_end = """
                 ) T
            GROUP BY account, account_name, analytic_account, analytic_account_name, tag
            ORDER BY tag, account::INTEGER
        """
        sql = sql_start + sql_budget_main + union + sql_budget_all + union + sql_balance_main + union + sql_balance_all \
            + sql_end
        params_budget = (context.get('date_from'),
                         context.get('date_to'), '(4|8|9)%')
        params_balance = (context.get('date_to'), context.get(
            'date_from'), 'posted', '(4|8|9)%', '(4|8|9)%',)
        self.env.cr.execute(sql, params_budget + params_balance)
        results = self.env.cr.dictfetchall()
        return results

    def _get_analytic_accounts(self):
        context = dict(self._context or {})

        sql = """
            SELECT AAA.code, AAA.name
            FROM account_analytic_account AAA
            JOIN crossovered_budget_lines CBL ON (CBL.analytic_account_id = AAA.id)
            WHERE CBL.date_from >= %s
            AND CBL.date_to <= %s
             GROUP BY AAA.code, AAA.name
             ORDER BY AAA.code::INTEGER;
         """

        params = (context.get('date_from'), context.get('date_to'))
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _get_grouped(self, options, line_id):
        # context = dict(self._context or {})

        account_grouped = collections.OrderedDict()

        results = self._do_query(options, line_id)
        for result in results:
            account_code = result['account']
            analytic_code = result['analytic_account']
            if account_code not in account_grouped:
                account_grouped[account_code] = {}
                account_grouped[account_code]['name'] = result['account_name']
                account_grouped[account_code]['tag'] = result['tag']
            account_grouped[account_code][analytic_code] = {
                'budget': result['budget_balance'], 'balance': result['balance']}
        return account_grouped

    def _get_lines(self, options, line_id=None):
        lines = []
        accounts_grouped = self._get_grouped(options, line_id)
        analytical_accounts = {values['code']: values['name'].replace(values['code'], '').strip() for values in
                               self._get_analytic_accounts()}
        account_groups_tag = {}
        accounts = len(analytical_accounts)
        if accounts:
            no_columns = accounts + 2
        else:
            no_columns = self.columns

        lines.append({
            'id': '5000',
            'name': '',
            'title_hover': '50000',
            'columns': [{'name': ''},
                        {'name': '50000',
                         'style': 'font-size:16px', 'colspan': no_columns * 4 - 4}],
            'level': 1,
            'unfoldable': False,
            'colspan': 1,
            'style': 'text-align:left;background-color:#ccc',
            'class': 'profit_center_50000_sticky_header'
        })

        columns_header2 = [{'name': ''}]
        for v in analytical_accounts:
            columns_header2 += [{'name': ''}]
            columns_header2 += [{'name': v, 'class': 'text-right'}]
            columns_header2 += [{'name': ''}, {'name': ''}]

        columns_header2 += [{'name': '', 'style': 'background-color:#fdfd76'},
                            {'name': 'Total 50000', 'class': 'text-right',
                                'style': 'background-color:#fdfd76'},
                            {'name': '', 'style': 'background-color:#fdfd76'},
                            {'name': '', 'style': 'background-color:#fdfd76'}]

        lines.append({
            'id': 'analytical_accounts_50000',
            'name': '',
            'title_hover': '50000',
            'columns': columns_header2,
            'level': 2,
            'unfoldable': False,
            'colspan': 1,
            'style': 'text-align:right;font-size:15px;background-color:lightblue',
            'class': '50000_sticky_header'
        })

        columns_header3 = [{'name': ''}]
        for v in analytical_accounts:
            columns_header3 += [{'name': ''}]
            columns_header3 += [{'name': analytical_accounts[v].strip()
                                 [0:18], 'class': 'text-right'}]
            columns_header3 += [{'name': ''}, {'name': ''}]

        columns_header3 += [{'name': '', 'style': 'background-color:#fdfd76'},
                            {'name': '', 'style': 'background-color:#fdfd76',
                                'class': 'text-right'},
                            {'name': '', 'style': 'background-color:#fdfd76'},
                            {'name': '', 'style': 'background-color:#fdfd76'}]

        lines.append({
            'id': 'analytical_account_name_50000',
            'name': '',
            'title_hover': '50000',
            'columns': columns_header3,
            'level': 2,
            'unfoldable': False,
            'colspan': 1,
            'style': 'text-align:right;font-size:10px;background-color:lightblue',
            'class': '50000_sticky_header'
        })

        lines.append({
            'id': 'analytical_account_name_comparison',
            'name': '',
            'title_hover': '',
            'columns': [{'name': ''}] + [{'name': 'BALANCE'}, {'name': 'BUDGET'}, {'name': 'DIFF'},
                                         {'name': '%'}] * len(analytical_accounts) +
            [{'name': 'BALANCE', 'style': 'background: lightyellow'},
             {'name': 'BUDGET', 'style': 'background: lightyellow'},
             {'name': 'DIFF', 'style': 'background: lightyellow'},
             {'name': '%', 'style': 'background: lightyellow'}],
            'level': 2,
            'unfoldable': False,
            'colspan': 1,
            'style': 'text-align:right;font-size:10px;background-color:LightCyan',
            'class': '50000_sticky_header'
        })
        current_tag = None
        i = 0
        # total_tag = {'budget': 0, 'balance': 0}
        # total_account = {'budget': 0, 'balance': 0}
        total_per_analytical_account = collections.OrderedDict()

        for account, values in accounts_grouped.items():
            if current_tag and current_tag != values['tag']:
                lines = self.add_total_tag(
                    account_groups_tag, current_tag, lines)

            if current_tag != values['tag']:
                current_tag = values['tag']
                # total_tag = {'budget': 0, 'balance': 0}

            if current_tag not in account_groups_tag:
                account_groups_tag[current_tag] = collections.OrderedDict()

            columns = []
            show_account = False
            total_per_account = {'budget': 0, 'balance': 0}

            for analytical_account in analytical_accounts:
                if analytical_account not in account_groups_tag[values['tag']]:
                    account_groups_tag[current_tag][analytical_account] = {
                        'budget': 0, 'balance': 0}
                if analytical_account not in total_per_analytical_account:
                    total_per_analytical_account[analytical_account] = {
                        'budget': 0, 'balance': 0}

                try:
                    if values[analytical_account]['balance'] != 0:
                        columns.append(
                            round(values[analytical_account]['balance'], 2))
                        total_per_account['balance'] += values[analytical_account]['balance']
                        total_per_analytical_account[analytical_account]['balance'] += values[analytical_account][
                            'balance']
                    else:
                        columns.append('')
                    if values[analytical_account]['budget'] != 0:
                        columns.append(
                            round(values[analytical_account]['budget'], 2))
                        total_per_account['budget'] += values[analytical_account]['budget']
                        total_per_analytical_account[analytical_account]['budget'] += values[analytical_account][
                            'budget']
                    else:
                        columns.append('')
                    if (values[analytical_account]['balance'] != 0) or (values[analytical_account]['budget'] != 0):
                        columns.append(
                            round(values[analytical_account]['balance'] - values[analytical_account]['budget'], 2))
                    else:
                        columns.append('')
                    if (values[analytical_account]['balance'] != 0) and (values[analytical_account]['budget'] != 0):
                        columns.append(round(
                            (values[analytical_account]['balance'] / values[analytical_account]['budget']) - 1, 2))
                    elif (values[analytical_account]['balance'] != 0) or (
                            values[analytical_account]['budget'] != 0):
                        columns.append(0)
                    else:
                        columns.append('')

                    account_groups_tag[current_tag][analytical_account]['budget'] += values[analytical_account][
                        'budget']
                    account_groups_tag[current_tag][analytical_account]['balance'] += values[analytical_account][
                        'balance']
                    if (values[analytical_account]['budget'] != 0) or (values[analytical_account]['balance'] != 0):
                        show_account = True
                except KeyError:
                    columns.append('')
                    columns.append('')
                    columns.append('')
                    columns.append('')

            if show_account:
                column_account = [{'name': values['name'], 'style': 'text-align:left'}] + \
                                 [{'name': v, 'style': 'margin-left:0;border-right:1px solid #f3f3f3'}
                                  for v in columns] + \
                                 [{'name': round(total_per_account['balance'], 2),
                                   'style': 'background-color:#ffffa6'},
                                  {'name': round(total_per_account['budget'], 2),
                                   'style': 'background-color:#ffffa6'},
                                  {'name': round(total_per_account['balance'] - total_per_account['budget'], 2),
                                   'style': 'background-color:#ffffa6'},
                                  {'name': round(
                                      (total_per_account['balance'] / total_per_account['budget']) - 1 if
                                      total_per_account['budget'] else 0,
                                      2),
                                      'style': 'background-color:#ffffa6'}
                                  ]
                lines.append({
                    'id': '50000',
                    'name': account,
                    'title_hover': account,
                    'columns': column_account,
                    'level': 3,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:right;width:10%'
                })

            i += 1
            if i == len(accounts_grouped):
                lines = self.add_total_tag(
                    account_groups_tag, current_tag, lines, False)

        totals = []
        for analytical_account in total_per_analytical_account:
            totals.append(
                total_per_analytical_account[analytical_account]['balance'])
            totals.append(
                total_per_analytical_account[analytical_account]['budget'])
            totals.append(total_per_analytical_account[analytical_account]['balance'] -
                          total_per_analytical_account[analytical_account]['budget'])
            totals.append((total_per_analytical_account[analytical_account]['balance'] /
                           total_per_analytical_account[analytical_account]['budget']) - 1 if
                          total_per_analytical_account[analytical_account]['budget'] else 0)
        total_per_analytical_account_balance = sum(
            [total_per_analytical_account[analytical_account]['balance'] for analytical_account in
             total_per_analytical_account])
        total_per_analytical_account_budget = sum(
            [total_per_analytical_account[analytical_account]['budget'] for analytical_account in
             total_per_analytical_account])
        columns_total = [{'name': ''}] + \
                        [{'name': round(v, 2) if v else '', 'style': 'font-size:13px'} for v in
                         totals] \
            + [{'name': round(total_per_analytical_account_balance, 2)},
               {'name': round(
                   total_per_analytical_account_budget, 2)},
               {'name': round(total_per_analytical_account_balance - total_per_analytical_account_budget,
                              2)},
               {'name': round((total_per_analytical_account_balance /
                               total_per_analytical_account_budget) - 1
                              if total_per_analytical_account_budget else 0, 2)}]
        lines.append({
            'id': 'total_50000',
            'name': 'TOTAL',
            'title_hover': '50000',
            'columns': columns_total,
            'level': 2,
            'unfoldable': False,
            'colspan': 1,
            'style': 'text-align:right;font-size:16px;background-color:#fdfd76'
        })
        empty_line = {
            'id': '50000_empty_line',
            'name': '',
            'title_hover': '',
            'columns': [{'name': ''} for i in range(len(total_per_analytical_account) + 2)],
            'level': 3,
            'unfoldable': False,
            'colspan': 1
        }
        lines.append(empty_line)
        print ("lines", lines)
        return lines

    def add_total_tag(self, account_groups_tag, current_tag, lines, empty_line=True):
        total_tag = account_groups_tag[current_tag]
        total_budget = sum([total_tag[analytical_account]['budget']
                            for analytical_account in total_tag])
        total_balance = sum([total_tag[analytical_account]['balance']
                             for analytical_account in total_tag])
        if total_balance != 0 or total_budget != 0:
            additional_columns = 4
            values = []
            for analytical_account in total_tag:
                values.append(total_tag[analytical_account]['balance'])
                values.append(total_tag[analytical_account]['budget'])
                values.append(
                    total_tag[analytical_account]['balance'] - total_tag[analytical_account]['budget'])
                values.append(
                    (total_tag[analytical_account]['balance'] / total_tag[analytical_account]['budget']) - 1 if
                    total_tag[analytical_account]['budget'] else 0)

            columns = [{'name': current_tag}] + \
                      [{'name': round(total_per_account, 2) if total_per_account != 0 else '',
                        'style': 'text-align:right;font-size:13px'}
                       for total_per_account in values] + \
                      [{'name': round(total_balance, 2),
                        'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}] + \
                      [{'name': round(total_budget, 2),
                        'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}] + \
                      [{'name': round(total_balance - total_budget, 2),
                        'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}] + \
                      [{'name': round((total_balance / total_budget) - 1 if total_budget else 0, 2),
                        'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]

            lines.append({
                'id': '{}'.format(current_tag),
                'name': '',
                'title_hover': current_tag,
                'columns': columns,
                'level': 1,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:left;font-size:16px;background-color:#f2f2f3'
            })

            if empty_line:
                lines.append({
                    'id': '{}_empty_line'.format(current_tag),
                    'name': '',
                    'title_hover': '',
                    'columns': [{'name': ''} for i in range(len(account_groups_tag[current_tag]) + additional_columns)],
                    'level': 3,
                    'unfoldable': False,
                    'colspan': 1
                })
        return lines
