# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dateutil import parser


class BudgetAnalysisReport(models.AbstractModel):
    _name = "budget.analysis.report2"
    _description = "Budget Analysis  Report"
    _inherit = "account.report"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month', 'mode': 'range'}
    filter_comparison = None
    filter_cash_basis = None
    filter_all_entries = None
    filter_hierarchy = None
    filter_unfold_all = None
    filter_multi_company = None
    filter_profit_center_accounts = None
    filter_encryption = None
    columns = 16

    @api.model
    def _get_report_name(self):
        return _("Budget Analysis Report")

    def _get_templates(self):
        templates = super(BudgetAnalysisReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    def _get_columns_name(self, options):
        # accounts = self._get_columns(options)
        # if accounts:
        #     columns = accounts * 3 + 10
        # else:
        columns = self.columns
        return [{'name': ''}] * (columns + 3)

    # def _get_columns(self, options):
    #     context = dict(self._context or {})
    #     sql = """
    #            SELECT count(*) as accounts FROM (
    #                SELECT DISTINCT analytical_account_id
    #                FROM budget_encryption_mapping_line
    #            ) AS A;
    #        """
    #     params = context.get('date_to'), context.get('date_to')
    #     self.env.cr.execute(sql, params)
    #     results = self.env.cr.dictfetchall()

    #     if results:
    #         return results[0]['accounts']
    #     else:
    #         return None

    def _get_profit_centers(self):
        context = dict(self._context or {})
        if 'date_from' and 'date_to' in context:
            date_to = context['date_to']
            date_from = context['date_from']
        else:
            today = datetime.today()
            dates = [("{:02d}".format(today.month), str(today.year))]

        where_list = []
        where_args = tuple()
        for date in dates:
            where_list.append("(BEM.month = %s AND BEM.year = %s)")
            where_args += date

        where = " AND ".join(where_list)
        sql = """
            SELECT 
                AAA.id, AAA.name
            FROM budget_encryption_mapping_line BEML 
                JOIN budget_encryption_mapping BEM ON (BEML.budget_encryption_mapping_id = BEM.id) 
                JOIN account_analytic_account AAA ON (AAA.id = BEML.cost_center) 
            WHERE {}
            GROUP BY AAA.id, AAA.name 
            ORDER BY AAA.code::INTEGER;
        """.format(where)

        self.env.cr.execute(sql, where_args)
        results = self.env.cr.dictfetchall()

        return {result['id']: result['name'] for result in results}

    def _get_analytic_accounts(self):
        context = dict(self._context or {})
        where_args = ['%s' for profit_center_id in context['profit_centers']]

        where_date, where_date_args = self._get_dates(context)

        sql = """
             SELECT 
                 AAA.code,
                 AAA.name    
             FROM budget_encryption_mapping_line BEML 
                 JOIN budget_encryption_mapping BEM ON (BEML.budget_encryption_mapping_id = BEM.id) 
                 JOIN account_analytic_account AAA ON (AAA.id = BEML.analytical_account_id) 
             WHERE ({}) 
                 AND BEML.cost_center IN ({})
             GROUP BY AAA.code, AAA.name
             ORDER BY AAA.code::INTEGER;
         """.format(where_date, ','.join(where_args))

        params_profit_center = tuple(profit_center_id for profit_center_id in context['profit_centers'])
        params = where_date_args + params_profit_center
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _get_dates(self, context):
        if 'date_from' and 'date_to' in context:
            date_to = parser.parse(context['date_to'])
            date_from = parser.parse(context['date_from'])
        else:
            date_to = date_from = datetime.today()
        dates = []
        for year in range(date_from.year, date_to.year + 1):
            start = 1
            end = 12
            if year == date_from.year:
                start = date_from.month
            elif year == date_to.year:
                end = date_to.month
            for month in range(start, end + 1):
                dates.append(("{:02d}".format(month), str(year)))
        where_list = []
        where_date_args = tuple()
        for date in dates:
            where_list.append("(BEM.month = %s AND BEM.year = %s)")
            where_date_args += date
        where_date = " OR ".join(where_list)
        return where_date, where_date_args

    def _do_query(self, options, line_id):
        context = dict(self._context or {})
        where_args = ['%s' for profit_center_id in context['profit_centers']]
        sql_start = """
                SELECT account,
                       account_name,
                       analytic_account,
                       analytic_account_name,
                       profit_center,
                       profit_center_name,
                       profit_center_code,
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
                   BEML.cost_center                          AS profit_center,
                   AAA_CC.name                               AS profit_center_name,
                   AAA_CC.code                               AS profit_center_code,
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
                   JOIN budget_encryption_mapping_line BEML ON (CBL.analytic_account_id = BEML.analytical_account_id)
                   JOIN budget_encryption_mapping BEM ON (BEML.budget_encryption_mapping_id = BEM.id
                                                            AND
                                                          TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD') <= CBL.date_from
                                                            AND (date_trunc('month',
                                                                            TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD')) +
                                                                 interval '1 month' - interval '1 day') >= CBL.date_to)
                   JOIN account_analytic_account AAA_CC ON (AAA_CC.id = BEML.cost_center)
            WHERE AAA_CC.id in ({})
              AND CBL.date_from >= %s
              AND CBL.date_to <= %s
              AND BEML.encryption > 0
        """.format(','.join(where_args))

        union = """ UNION ALL """

        sql_budget_all = """
                    SELECT DISTINCT
                           AA.code     AS account,
                           AA.name     AS account_name,
                           AAT.name    AS tag,
                           ''          AS analytic_account,
                           ''          AS analytic_account_name,
                           AAA_BEM.id   AS profit_center,
                           AAA_BEM.name AS profit_center_name,
                           AAA_BEM.code AS profit_center_code,
                           0            AS budget_balance,
                           0           AS balance
                    FROM account_account AA
                           JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AA.id)
                           JOIN account_account_tag AAT ON (AAAT.account_account_tag_id = AAT.id)
                           CROSS JOIN account_analytic_account AAA_BEM
                    WHERE AA.code SIMILAR TO %s
                      AND AA.code != '999999'
                      AND AA.deprecated = FALSE
                      AND AAA_BEM.id IN ({})
                """.format(','.join(where_args))

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
        params_profit_center = tuple(profit_center_id for profit_center_id in context['profit_centers'])
        params_budget = params_profit_center + (context.get('date_from'), context.get('date_to'), '(4|8|9)%') + \
                        params_profit_center
        params_balance = (context.get('date_to'), context.get('date_from'), 'posted', '(4|8|9)%',
                          context.get('date_to'), context.get('date_to')) + params_profit_center + ('(4|8|9)%',) + \
                         params_profit_center
        self.env.cr.execute(sql, params_budget + params_balance)
        results = self.env.cr.dictfetchall()
        return results

    def _get_grouped_profit_center(self, options, line_id):
        context = dict(self._context or {})
        profit_centers = context.get('profit_centers')

        accounts_per_profit_center = collections.OrderedDict(
            {pc_id: {'accounts': collections.OrderedDict()} for pc_id in profit_centers})

        results = self._do_query(options, line_id)
        for result in results:
            pc_code = result['profit_center_code']
            pc_id = result['profit_center']
            pc_name = result['profit_center_name']
            accounts_per_profit_center[pc_id]['name'] = pc_name
            account_code = result['account']
            analytic_code = result['analytic_account']
            accounts_per_profit_center[pc_id]['name'] = pc_name
            accounts_per_profit_center[pc_id]['code'] = pc_code
            if account_code not in accounts_per_profit_center[pc_id]['accounts']:
                accounts_per_profit_center[pc_id]['accounts'][account_code] = {}
                accounts_per_profit_center[pc_id]['accounts'][account_code]['name'] = result['account_name']
                accounts_per_profit_center[pc_id]['accounts'][account_code]['tag'] = result['tag']
            accounts_per_profit_center[pc_id]['accounts'][account_code][analytic_code] = {
                'budget': result['budget_balance'], 'balance': result['balance']}
        return accounts_per_profit_center

    def _do_query_cc6(self, pc_code):
        sql_budget = """
               SELECT AA.code                            AS account,
                       AAA_CC.name                               AS profit_center_name,
                       CBL.planned_amount * BEML.encryption / 100 AS budget_balance,
                       0                                AS balance
                FROM crossovered_budget CB
                       JOIN crossovered_budget_lines CBL ON (CB.id = CBL.crossovered_budget_id)
                       JOIN account_budget_post ABP ON (CBL.general_budget_id = ABP.id)
                       JOIN account_budget_rel ABR ON (ABP.id = ABR.budget_id)
                       JOIN account_account AA ON (AA.id = ABR.account_id)
                       JOIN budget_encryption_mapping_line BEML ON (CBL.analytic_account_id = BEML.analytical_account_id)
                       JOIN budget_encryption_mapping BEM ON (BEML.budget_encryption_mapping_id = BEM.id
                                                                AND
                                                              TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD') <= CBL.date_from
                                                                AND (date_trunc('month',
                                                                                TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD')) +
                                                                     interval '1 month' - interval '1 day') >= CBL.date_to)
                       JOIN account_analytic_account AAA_CC ON (AAA_CC.id = BEML.cost_center)
                WHERE AAA_CC.code = %s
                  AND CBL.date_from >= %s
                  AND CBL.date_to <= %s
                  AND BEML.encryption > 0
           """

        sql_balance = """
            SELECT AA.code     AS account,
                   AAA_EM.name AS profit_center_name,
                   0            AS budget_balance,
                   EML.encryption / 100 * balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END) 
                   AS balance
            FROM encryption_mapping_line EML
                     JOIN encryption_mapping EM ON (EML.encryption_mapping_id = EM.id)
                     JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)
                     JOIN account_analytic_account AAA_EM ON (AAA_EM.id = EML.cost_center)
                     JOIN account_move_line AML ON (AML.analytic_account_id = EML.analytical_account_id)
                     JOIN account_account AA ON (AML.account_id = AA.id)
                     JOIN account_analytic_account AAA ON (AAA.id = AML.analytic_account_id)
                     JOIN account_move AM ON (AM.id = AML.move_id)
                     LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                AND RCR.name = date_trunc('month', AML.date)::date)
            WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
              AND AML.date <= %s
              AND AML.date >= %s
              AND AM.state = %s
              AND AA.code SIMILAR TO %s
              AND AA.code != '999999'
              AND AFY.date_to >= %s
              AND AFY.date_from <= %s
                AND AAA_EM.code = %s
        """
        sql = """
            SELECT account, 
                    profit_center_name, 
                    SUM(budget_balance) AS budget_balance,
                    SUM(balance) AS balance
                      FROM (
                {} UNION ALL {}) AS T
                GROUP BY account, profit_center_name
        """.format(sql_balance, sql_budget)
        context = dict(self._context or {})
        params_budget = pc_code, context.get('date_from'), context.get('date_to')
        params_balance = context.get('date_to'), context.get('date_from'), 'posted', '(4|8|9)%', \
                         context.get('date_to'), context.get('date_to'), pc_code
        self.env.cr.execute(sql, (params_balance + params_budget))
        results = self.env.cr.dictfetchall()
        return results

    def _get_totals_cc6(self, pc_code):
        results = self._do_query_cc6(pc_code)
        totals_cc6 = {}
        pc_name = None
        for result in results:
            account = result['account']
            pc_name = result['profit_center_name']
            totals_cc6[account] = {'balance': result['balance'], 'budget': result['budget_balance']}
        try:
            pc_name = pc_name.replace(pc_code, '').strip()
        except AttributeError:
            pc_name = ''
        return totals_cc6, pc_name

    def _get_count_cc(self, accounts_grouped):
        count_cc6 = count_cc7 = 0
        last_cc6 = last_cc7 = None
        for pc in accounts_grouped:
            try:
                if accounts_grouped[pc]['code'][0] == '6':
                    count_cc6 += 1
                    last_cc6 = accounts_grouped[pc]['code']
                elif accounts_grouped[pc]['code'][0] == '7':
                    count_cc7 += 1
                    last_cc7 = accounts_grouped[pc]['code']
            except KeyError:
                pass
        return count_cc6, count_cc7, last_cc6, last_cc7

    def _get_lines(self, options, line_id=None):
        lines = []
        accounts_grouped = self._get_grouped_profit_center(options, line_id)
        analytical_accounts = {values['code']: values['name'].replace(values['code'], '').strip() for values in
                               self._get_analytic_accounts()}
        count_cc6, count_cc7, last_cc6, last_cc7 = self._get_count_cc(accounts_grouped)
        total_per_analytical_account_cc6_balance = collections.Counter()
        total_per_analytical_account_cc6_budget = collections.Counter()
        total_per_analytical_account_cc7_balance = collections.Counter()
        total_per_analytical_account_cc7_budget = collections.Counter()
        total_all_cc6 = {'balance': 0, 'budget': 0}
        columns_total_cc = []
        for pc in accounts_grouped:
            if len(accounts_grouped[pc]) < 2:
                continue
            account_groups_tag = {}
            accounts = len(analytical_accounts)
            if accounts:
                no_columns = accounts + 2
            else:
                no_columns = self.columns

            if accounts_grouped[pc]['code'][0] == '7':
                cc6_code = accounts_grouped[pc]['code'][:0] + '6' + accounts_grouped[pc]['code'][1:]
                totals_cc6, cc6_name = self._get_totals_cc6(cc6_code)
                no_columns += 2

            class_name = re.sub(r'\W+', '', accounts_grouped[pc]['name'].replace(' ', '_'))
            lines.append({
                'id': pc,
                'name': '',
                'title_hover': accounts_grouped[pc]['name'],
                'columns': [{'name': ''},
                            {'name': accounts_grouped[pc]['name'],
                             'style': 'font-size:16px', 'colspan': no_columns * 3 - 3}],
                'level': 1,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:left;background-color:#ccc',
                'class': 'profit_center_{}_sticky_header'.format(class_name)
            })

            columns_header2 = [{'name': ''}] + [{'name': v, 'colspan': 3} for v in analytical_accounts] + \
                              [{'name': 'Total {}'.format(accounts_grouped[pc]['code']), 'colspan': 3,
                                'style': 'background-color:#fdfd76'}]
            if accounts_grouped[pc]['code'][0] == '7':
                columns_header2 += [
                    {'name': 'TOTAL {}'.format(cc6_code), 'style': 'background-color:#fdfd76', 'colspan': 3}]
                columns_header2 += [{'name': 'TOTAL', 'style': 'background-color:#fdfd76', 'colspan': 3}]

            lines.append({
                'id': 'analytical_accounts_{}'.format(pc),
                'name': '',
                'title_hover': accounts_grouped[pc]['name'],
                'columns': columns_header2,
                'level': 2,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:center;font-size:15px;background-color:lightblue',
                'class': 'profit_center_{}_sticky_header'.format(class_name)
            })
            columns_header3 = [{'name': ''}] + \
                              [{'name': analytical_accounts[v].strip() if len(analytical_accounts[v].strip()) <= 18
                              else analytical_accounts[v].strip()[0:18], 'colspan': 3}
                               for v in analytical_accounts] + [
                                  {'name': '', 'style': 'background-color:#fdfd76', 'colspan': 3}]
            if accounts_grouped[pc]['code'][0] == '7':
                columns_header3 += [{'name': cc6_name, 'style': 'background-color:#fdfd76', 'colspan': 3}]
                columns_header3 += [{'name': '{} + {}'.format(cc6_code, accounts_grouped[pc]['code']),
                                     'style': 'background-color:#fdfd76', 'colspan': 3}]

            lines.append({
                'id': 'analytical_account_name_{}'.format(pc),
                'name': '',
                'title_hover': accounts_grouped[pc]['name'],
                'columns': columns_header3,
                'level': 2,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:center;font-size:10px;background-color:lightblue',
                'class': 'profit_center_{}_sticky_header'.format(class_name)
            })
            lines.append({
                'id': 'analytical_account_name_comparison',
                'name': '',
                'title_hover': '',
                'columns': [{'name': ''}] + [{'name': 'BALANCE'}, {'name': 'BUDGET'}, {'name': '%'}] * len(
                    analytical_accounts) + [{'name': 'BALANCE', 'style': 'background: lightyellow'},
                                            {'name': 'BUDGET', 'style': 'background: lightyellow'},
                                            {'name': '%', 'style': 'background: lightyellow'}] * (
                               3 if accounts_grouped[pc]['code'][0] == '7' else 1),
                'level': 2,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:right;font-size:10px;background-color:LightCyan',
                'class': 'profit_center_{}_sticky_header'.format(class_name)
            })
            current_tag = None
            i = 0
            total_cc6_tag = {'budget': 0, 'balance': 0}
            total_cc6 = {'budget': 0, 'balance': 0}
            total_cc6_account = {'budget': 0, 'balance': 0}
            total_per_analytical_account = collections.OrderedDict()
            for account, values in accounts_grouped[pc]['accounts'].items():
                if current_tag and current_tag != values['tag']:
                    lines = self.add_total_tag(account_groups_tag, current_tag, lines, pc, accounts_grouped[pc]['code'],
                                               total_cc6_tag)
                if accounts_grouped[pc]['code'][0] == '7':
                    try:
                        total_cc6_account = totals_cc6[account]
                    except KeyError:
                        total_cc6_account = {'budget': 0, 'balance': 0}

                if current_tag != values['tag']:
                    current_tag = values['tag']
                    total_cc6_tag = {'budget': 0, 'balance': 0}

                if current_tag not in account_groups_tag:
                    account_groups_tag[current_tag] = collections.OrderedDict()

                columns = []
                show_account = False
                total_per_account = {'budget': 0, 'balance': 0}

                for analytical_account in analytical_accounts:
                    if analytical_account not in account_groups_tag[values['tag']]:
                        account_groups_tag[current_tag][analytical_account] = {'budget': 0, 'balance': 0}
                    if analytical_account not in total_per_analytical_account:
                        total_per_analytical_account[analytical_account] = {'budget': 0, 'balance': 0}

                    try:
                        if values[analytical_account]['balance'] != 0:
                            columns.append(round(values[analytical_account]['balance'], 2))
                            total_per_account['balance'] += values[analytical_account]['balance']
                            total_per_analytical_account[analytical_account]['balance'] += values[analytical_account][
                                'balance']
                        else:
                            columns.append('')
                        if values[analytical_account]['budget'] != 0:
                            columns.append(round(values[analytical_account]['budget'], 2))
                            total_per_account['budget'] += values[analytical_account]['budget']
                            total_per_analytical_account[analytical_account]['budget'] += values[analytical_account][
                                'budget']
                        else:
                            columns.append('')
                        if (values[analytical_account]['balance'] != 0) and (values[analytical_account]['budget'] != 0):
                            columns.append(round(
                                100 * values[analytical_account]['balance'] / values[analytical_account]['budget'], 2))
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

                if accounts_grouped[pc]['code'][0] == '7':
                    total_cc6_tag['balance'] += total_cc6_account['balance']
                    total_cc6_tag['budget'] += total_cc6_account['budget']
                    total_cc6['balance'] += total_cc6_account['balance']
                    total_cc6['budget'] += total_cc6_account['budget']
                    if total_cc6_account['balance'] or total_cc6_account['budget']:
                        show_account = True

                if show_account:
                    column_account = [{'name': values['name'], 'style': 'text-align:left'}] + \
                                     [{'name': v, 'style': 'margin-left:0;border-right:1px solid #f3f3f3'}
                                      for v in columns] + \
                                     [{'name': round(total_per_account['balance'], 2),
                                       'style': 'background-color:#ffffa6'},
                                      {'name': round(total_per_account['budget'], 2),
                                       'style': 'background-color:#ffffa6'},
                                      {'name': round(
                                          (100 * total_per_account['balance'] / total_per_account['budget']) if
                                          total_per_account['budget'] else 0,
                                          2),
                                          'style': 'background-color:#ffffa6'}
                                      ]
                    if accounts_grouped[pc]['code'][0] == '7':
                        column_account += [{'name': round(total_cc6_account['balance'], 2),
                                            'style': 'background-color:#ffffa6'}]
                        column_account += [{'name': round(total_cc6_account['budget'], 2),
                                            'style': 'background-color:#ffffa6'}]
                        column_account += [
                            {'name': round(
                                (100 * total_cc6_account['balance'] / total_cc6_account['budget']) if total_cc6_account[
                                    'budget'] else 0, 2),
                                'style': 'background-color:#ffffa6'}]
                        column_account += [
                            {'name': round(total_cc6_account['balance'] + total_per_account['balance'], 2),
                             'style': 'background-color:#ffffa6'}]
                        column_account += [
                            {'name': round(total_cc6_account['budget'] + total_per_account['budget'], 2),
                             'style': 'background-color:#ffffa6'}]
                        column_account += [
                            {'name': round((100 * (total_cc6_account['balance'] + total_per_account['balance']) / (
                                    total_cc6_account['budget'] + total_per_account['budget'])) if (
                                    total_cc6_account['budget'] + total_per_account['budget']) else 0, 2),
                             'style': 'background-color:#ffffa6'}]

                    lines.append({
                        'id': pc,
                        'name': account,
                        'title_hover': account,
                        'columns': column_account,
                        'level': 3,
                        'unfoldable': False,
                        'colspan': 1,
                        'style': 'text-align:right;width:10%'
                    })

                i += 1
                if i == len(accounts_grouped[pc]['accounts']):
                    lines = self.add_total_tag(account_groups_tag, current_tag, lines, pc,
                                               accounts_grouped[pc]['code'][0], total_cc6_tag, False)

            totals = []
            for analytical_account in total_per_analytical_account:
                totals.append(total_per_analytical_account[analytical_account]['balance'])
                totals.append(total_per_analytical_account[analytical_account]['budget'])
                totals.append((100 * total_per_analytical_account[analytical_account]['balance'] /
                               total_per_analytical_account[analytical_account]['budget']) if
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
                               {'name': round(total_per_analytical_account_budget, 2)},
                               {'name': round((100 * total_per_analytical_account_balance /
                                               total_per_analytical_account_budget)
                                              if total_per_analytical_account_budget else 0, 2)}]

            if accounts_grouped[pc]['code'][0] == '7':
                total_cc6_balance = sum([totals_cc6[account]['balance'] for account in totals_cc6])
                total_cc6_budget = sum([totals_cc6[account]['budget'] for account in totals_cc6])
                columns_total += [{'name': round(total_cc6_balance, 2)}, {'name': round(total_cc6_budget, 2)},
                                  {'name': round(
                                      (100 * total_cc6_balance / total_cc6_budget) if total_cc6_budget else 0, 2)}]
                columns_total += [{'name': round(total_cc6_balance + total_per_analytical_account_balance, 2)},
                                  {'name': round(total_cc6_budget + total_per_analytical_account_budget, 2)},
                                  {'name': round((100 * (total_cc6_balance + total_per_analytical_account_balance) /
                                                  (total_cc6_budget + total_per_analytical_account_budget)) if (
                                          total_cc6_budget + total_per_analytical_account_budget) else 0, 2)}]

                total_per_analytical_account_cc7_balance.update(collections.Counter(
                    {analytical_account: total_per_analytical_account[analytical_account]['balance'] for
                     analytical_account in total_per_analytical_account}))
                total_per_analytical_account_cc7_budget.update(collections.Counter(
                    {analytical_account: total_per_analytical_account[analytical_account]['budget'] for
                     analytical_account in total_per_analytical_account}))
                total_all_cc6['balance'] += total_cc6['balance']
                total_all_cc6['budget'] += total_cc6['budget']
            else:
                total_per_analytical_account_cc6_balance.update(collections.Counter(
                    {analytical_account: total_per_analytical_account[analytical_account]['balance'] for
                     analytical_account in total_per_analytical_account}))
                total_per_analytical_account_cc6_budget.update(collections.Counter(
                    {analytical_account: total_per_analytical_account[analytical_account]['budget'] for
                     analytical_account in total_per_analytical_account}))

            lines.append({
                'id': 'total_{}'.format(pc),
                'name': 'TOTAL',
                'title_hover': accounts_grouped[pc]['name'],
                'columns': columns_total,
                'level': 2,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:right;font-size:16px;background-color:#fdfd76'
            })
            empty_line = {
                'id': '{}_empty_line'.format(pc),
                'name': '',
                'title_hover': '',
                'columns': [{'name': ''} for i in range(len(total_per_analytical_account) + 2)],
                'level': 3,
                'unfoldable': False,
                'colspan': 1
            }
            lines.append(empty_line)

            if count_cc6 > 1 and accounts_grouped[pc]['code'] == last_cc6:
                totals_combined = []
                for analytical_account in total_per_analytical_account_cc6_balance:
                    totals_combined.append(total_per_analytical_account_cc6_balance[analytical_account])
                    totals_combined.append(total_per_analytical_account_cc6_budget[analytical_account])
                    totals_combined.append((100 * total_per_analytical_account_cc6_balance[analytical_account] /
                                            total_per_analytical_account_cc6_budget[analytical_account]) if
                                           total_per_analytical_account_cc6_budget[analytical_account] else 0)
                sum_total_balance = sum(total_per_analytical_account_cc6_balance.values())
                sum_total_budget = sum(total_per_analytical_account_cc6_budget.values())
                columns_total_cc = [{'name': ''}] + \
                                   [{'name': round(v, 2) if v else '', 'style': 'font-size:13px'} for v in
                                    totals_combined] \
                                   + [{'name': round(sum_total_balance, 2)}] + [{'name': round(sum_total_budget, 2)}] \
                                   + [{'name': round(
                    (100 * sum_total_balance / sum_total_budget) if sum_total_budget else 0, 2)}]
                cc_name = "Total CC6"
            elif count_cc7 > 1 and accounts_grouped[pc]['code'] == last_cc7:
                totals_combined = []
                for analytical_account in total_per_analytical_account_cc7_balance:
                    totals_combined.append(total_per_analytical_account_cc7_balance[analytical_account])
                    totals_combined.append(total_per_analytical_account_cc7_budget[analytical_account])
                    totals_combined.append((100 * total_per_analytical_account_cc7_balance[analytical_account] /
                                            total_per_analytical_account_cc7_budget[analytical_account]) if
                                           total_per_analytical_account_cc7_budget[analytical_account] else 0)
                sum_total_balance = sum(total_per_analytical_account_cc7_balance.values())
                sum_total_budget = sum(total_per_analytical_account_cc7_budget.values())

                columns_total_cc = [{'name': ''}] + \
                                   [{'name': round(v, 2) if v else '', 'style': 'font-size:13px'} for v in
                                    totals_combined] \
                                   + [{'name': round(sum_total_balance, 2)},
                                      {'name': round(sum_total_budget, 2)},
                                      {'name': round(
                                          (100 * sum_total_balance / sum_total_budget) if sum_total_budget else 0, 2)},
                                      {'name': round(total_all_cc6['balance'], 2)},
                                      {'name': round(total_all_cc6['budget'], 2)},
                                      {'name': round(
                                          (100 * total_all_cc6['balance'] / total_all_cc6['budget']) if total_all_cc6[
                                              'budget'] else 0, 2)},
                                      {'name': round(total_all_cc6['balance'] + sum_total_balance, 2)},
                                      {'name': round(total_all_cc6['budget'] + sum_total_budget, 2)},
                                      {'name': round((100 * (total_all_cc6['balance'] + sum_total_balance) / (
                                                  total_all_cc6['budget'] + sum_total_budget)) if (
                                                  total_all_cc6['budget'] + sum_total_budget) else 0, 2)}
                                      ]
                cc_name = "Total CC7"

            if columns_total_cc:
                lines.append({
                    'id': 'total_{}'.format(pc),
                    'name': cc_name,
                    'title_hover': cc_name,
                    'columns': columns_total_cc,
                    'level': 2,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:right;font-size:16px;background-color:#fd9050'
                })
                lines.append(empty_line)
                lines.append(empty_line)
                columns_total_cc = []

            lines.append(empty_line)
        return lines

    def add_total_tag(self, account_groups_tag, current_tag, lines, profit_center, pc_code, total_cc6,
                      empty_line=True):
        total_tag = account_groups_tag[current_tag]
        total_budget = sum([total_tag[analytical_account]['budget'] for analytical_account in total_tag])
        total_balance = sum([total_tag[analytical_account]['balance'] for analytical_account in total_tag])
        if (total_balance != 0 or total_budget != 0) or (pc_code[0] == '7' and (total_cc6['balance'] != 0 or
                                                                                total_cc6['budget'] != 0)):
            additional_columns = 4
            values = []
            for analytical_account in total_tag:
                values.append(total_tag[analytical_account]['balance'])
                values.append(total_tag[analytical_account]['budget'])
                values.append(
                    (100 * total_tag[analytical_account]['balance'] / total_tag[analytical_account]['budget']) if
                    total_tag[analytical_account]['budget'] else 0)

            columns = [{'name': current_tag}] + \
                      [{'name': round(total_per_account, 2) if total_per_account != 0 else '',
                        'style': 'text-align:right;font-size:13px'}
                       for total_per_account in values] + \
                      [{'name': round(total_balance, 2),
                        'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}] + \
                      [{'name': round(total_budget, 2),
                        'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}] + \
                      [{'name': round((100 * total_balance / total_budget) if total_budget else 0, 2),
                        'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]

            if pc_code[0] == '7':
                columns += [{'name': round(total_cc6['balance'], 2),
                             'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
                columns += [{'name': round(total_cc6['budget'], 2),
                             'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
                columns += [
                    {'name': round((100 * total_cc6['balance'] / total_cc6['budget']) if total_cc6['budget'] else 0, 2),
                     'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
                columns += [{'name': round(total_cc6['balance'] + total_balance, 2),
                             'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
                columns += [{'name': round(total_cc6['budget'] + total_budget, 2),
                             'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
                columns += [{'name': round((100 * (total_cc6['balance'] + total_balance) / (total_cc6['budget'] +
                                            total_budget)) if (total_cc6['budget'] + total_budget) else 0, 2),
                             'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
                additional_columns = 10
            lines.append({
                'id': '{}_{}'.format(profit_center, current_tag),
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
                    'id': '{}_{}_empty_line'.format(profit_center, current_tag),
                    'name': '',
                    'title_hover': '',
                    'columns': [{'name': ''} for i in range(len(account_groups_tag[current_tag]) + additional_columns)],
                    'level': 3,
                    'unfoldable': False,
                    'colspan': 1
                })
        return lines
