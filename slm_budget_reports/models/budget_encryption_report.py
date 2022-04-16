# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, api, _
from datetime import datetime
from dateutil import parser
from odoo.exceptions import ValidationError


class BudgetEncryptionReport(models.AbstractModel):
    _name = "budget.encryption.report"
    _description = "Budget Encryption Report"
    _inherit = "account.report"

    filter_date = {'date_from': '', 'date_to': '',
                   'filter': 'this_month', 'mode': 'range'}
    filter_comparison = None
    filter_cash_basis = None
    filter_all_entries = None
    filter_hierarchy = None
    filter_unfold_all = None
    filter_multi_company = None
    filter_profit_center_accounts = True
    filter_encryption = True
    columns = 100

    @api.model
    def _get_report_name(self):
        return _("Budget Encryption Report")

    def _get_templates(self):
        templates = super(BudgetEncryptionReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    def _get_columns_name(self, options):
        # accounts = self._get_columns(options)
        # if accounts:
        #     columns = accounts + 2
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

    def _set_context(self, options):
        ctx = super(BudgetEncryptionReport, self)._set_context(options)
        profit_centers = []
        encryptions = []
        if options.get('profit_center_accounts'):
            profit_centers = [
                c.get('id') for c in options['profit_center_accounts'] if c.get('selected')]
            profit_centers = profit_centers if len(profit_centers) > 0 else [c.get('id')
                                                                             for c in options['profit_center_accounts']]
        ctx['profit_centers'] = len(profit_centers) > 0 and profit_centers

        if options.get('encryption'):
            encryptions = [c.get('id')
                           for c in options['encryption'] if c.get('selected')]
            encryptions = encryptions if len(encryptions) > 0 else [c.get('id')
                                                                    for c in options['encryption']]
        ctx['encryptions'] = len(encryptions) > 0 and encryptions

        return ctx

    def _get_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = super(BudgetEncryptionReport,
                        self)._get_options(previous_options)
        if options.get('profit_center_accounts'):
            profit_centers = self._get_profit_centers()
            options['profit_center_accounts'] = [{'id': id, 'name': profit_centers[id], 'selected': False}
                                                 for id in profit_centers]

        if options.get('encryption'):
            encryptions = {'cc5_cc6': 'CC5 to CC6', 'cc6_cc7': 'CC6 to CC7'}
            options['encryption'] = [
                {'id': i, 'name': v, 'selected': False} for i, v in encryptions.items()]

        # Merge old options with default from this report
        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                if key in ['profit_center_accounts', 'encryption']:
                    options[key] = previous_options[key]

        return options

    def _get_profit_centers(self):
        # context = dict(self._context or {})
        # if 'date_from' and 'date_to' in context:
        #     date_to = context['date_to']
        #     date_from = context['date_from']
        # else:
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

        month, year = list(where_args)[0], list(where_args)[1]
        self.env.cr.execute(sql, where_args)
        results = self.env.cr.dictfetchall()
        if not results:
            raise ValidationError(_("There is no Budget Encryption Mapping data found for %s month and %s year") % (month, year))
        else:
            return {result['id']: result['name'] for result in results}

    def _get_analytic_accounts(self):
        context = dict(self._context or {})
        pc = self._get_profit_centers()
        profit_centers1 = [{'id': id, 'name': pc[id], 'selected': False} for id in pc]
        profit_centers2 = [c.get('id') for c in profit_centers1 if c.get('selected')]
        profit_centers = profit_centers2 if len(profit_centers2) > 0 else [c.get('id') for c in profit_centers1]
        context['profit_centers'] = profit_centers
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

        params_profit_center = tuple(
            profit_center_id for profit_center_id in context['profit_centers'])
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
        profit_centers = []
        if options.get('profit_center_accounts'):
            profit_centers = [
                c.get('id') for c in options['profit_center_accounts'] if c.get('selected')]
            profit_centers = profit_centers if len(profit_centers) > 0 else [c.get('id')
                                                                             for c in options['profit_center_accounts']]
        context['profit_centers'] = len(profit_centers) > 0 and profit_centers
        where_args = ['%s' for profit_center_id in context['profit_centers']]
        sql_start = """
                        SELECT account, account_name, analytic_account, analytic_account_name,
                            profit_center, profit_center_name, profit_center_code,
                            sum(balance) as balance, tag
                        FROM (
                """

        sql_main = """
            SELECT AA.code                                   AS account,
                   AA.name                                   AS account_name,
                   AAT.name                                  AS tag,
                   AAA.code                                  AS analytic_account,
                   AAA.name                                  AS analytic_account_name,
                   BEML.cost_center                          AS profit_center,
                   AAA_CC.name                               AS profit_center_name,
                   AAA_CC.code                               AS profit_center_code,
                   SUM(CBL.planned_amount * (BEML.encryption/100)) AS balance
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
            GROUP BY AA.code, AA.name, AAT.name, AAA.code, AAA.name, BEML.cost_center, AAA_CC.name, AAA_CC.code
        """.format(','.join(where_args))

        union = """ UNION ALL """

        sql_all = """
                    SELECT DISTINCT
                           AA.code     AS account,
                           AA.name     AS account_name,
                           AAT.name    AS tag,
                           ''          AS analytic_account,
                           ''          AS analytic_account_name,
                           AAA_BEM.id   AS profit_center,
                           AAA_BEM.name AS profit_center_name,
                           AAA_BEM.code AS profit_center_code,
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

        sql_end = """
                   ) AS A
                       GROUP BY account, account_name, analytic_account, analytic_account_name,
                                profit_center, profit_center_name, profit_center_code, tag
                       ORDER BY profit_center_name, tag, account::INTEGER
               """

        sql = sql_start + sql_main + union + sql_all + sql_end

        params_profit_center = tuple(
            profit_center_id for profit_center_id in context['profit_centers'])
        params = params_profit_center + (context.get('date_from'), context.get('date_to'), '(4|8|9)%') + \
            params_profit_center
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _get_grouped_profit_center(self, options, line_id):
        context = dict(self._context or {})
        profit_centers = []
        profit_centers = context.get('profit_centers')
        if options.get('profit_center_accounts'):
            profit_centers = [
                c.get('id') for c in options['profit_center_accounts'] if c.get('selected')]
            profit_centers = profit_centers if len(profit_centers) > 0 else [c.get('id')
                                                                             for c in options['profit_center_accounts']]
        context['profit_centers'] = len(profit_centers) > 0 and profit_centers
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
                accounts_per_profit_center[pc_id]['accounts'][account_code] = {
                }
                accounts_per_profit_center[pc_id]['accounts'][account_code]['name'] = result['account_name']
                accounts_per_profit_center[pc_id]['accounts'][account_code]['tag'] = result['tag']
            accounts_per_profit_center[pc_id]['accounts'][account_code][analytic_code] = result['balance']
        return accounts_per_profit_center

    def _do_query_cc6(self, pc_code):
        sql = """
               SELECT AA.code                            AS account,
                       AAA_CC.name                               AS profit_center_name,
                       SUM(CBL.planned_amount * BEML.encryption / 100) AS balance
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
                GROUP BY AA.code, AAA_CC.name
           """
        context = dict(self._context or {})
        params = pc_code, context.get('date_from'), context.get('date_to')
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _get_totals_cc6(self, pc_code):
        results = self._do_query_cc6(pc_code)
        totals_cc6 = {}
        pc_name = None
        for result in results:
            account = result['account']
            pc_name = result['profit_center_name']
            totals_cc6[account] = result['balance']
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
        count_cc6, count_cc7, last_cc6, last_cc7 = self._get_count_cc(
            accounts_grouped)
        total_per_analytical_account_cc6 = collections.Counter()
        total_per_analytical_account_cc7 = collections.Counter()
        total_all_cc6 = 0
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
                cc6_code = accounts_grouped[pc]['code'][:0] + \
                    '6' + accounts_grouped[pc]['code'][1:]
                totals_cc6, cc6_name = self._get_totals_cc6(cc6_code)
                no_columns += 2

            class_name = re.sub(
                r'\W+', '', accounts_grouped[pc]['name'].replace(' ', '_'))
            lines.append({
                'id': pc,
                'name': '',
                'title_hover': accounts_grouped[pc]['name'],
                'columns': [{'name': ''},
                            {'name': accounts_grouped[pc]['name'],
                             'style': 'font-size:16px', 'colspan': no_columns - 1}],
                'level': 1,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:left;background-color:#ccc',
                'class': 'profit_center_{}_sticky_header'.format(class_name)
            })

            columns_header2 = [{'name': ''}] + [{'name': v} for v in analytical_accounts] + \
                              [{'name': 'Total {}'.format(accounts_grouped[pc]['code']),
                                'style': 'background-color:#fdfd76'}]
            if accounts_grouped[pc]['code'][0] == '7':
                columns_header2 += [{'name': 'TOTAL {}'.format(
                    cc6_code), 'style': 'background-color:#fdfd76'}]
                columns_header2 += [{'name': 'TOTAL',
                                     'style': 'background-color:#fdfd76'}]

            lines.append({
                'id': 'analytical_accounts_{}'.format(pc),
                'name': '',
                'title_hover': accounts_grouped[pc]['name'],
                'columns': columns_header2,
                'level': 2,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:right;font-size:15px;background-color:lightblue',
                'class': 'profit_center_{}_sticky_header'.format(class_name)
            })
            columns_header3 = [{'name': ''}] + \
                              [{'name': analytical_accounts[v].strip() if len(analytical_accounts[v].strip()) <= 18
                                else analytical_accounts[v].strip()[0:18]}
                               for v in analytical_accounts] + [{'name': '', 'style': 'background-color:#fdfd76'}]
            if accounts_grouped[pc]['code'][0] == '7':
                columns_header3 += [{'name': cc6_name,
                                     'style': 'background-color:#fdfd76'}]
                columns_header3 += [{'name': '{} + {}'.format(cc6_code, accounts_grouped[pc]['code']),
                                     'style': 'background-color:#fdfd76'}]

            lines.append({
                'id': 'analytical_account_name_{}'.format(pc),
                'name': '',
                'title_hover': accounts_grouped[pc]['name'],
                'columns': columns_header3,
                'level': 2,
                'unfoldable': False,
                'colspan': 1,
                'style': 'text-align:right;font-size:10px;background-color:lightblue',
                'class': 'profit_center_{}_sticky_header'.format(class_name)
            })
            current_tag = None
            i = 0
            total_cc6_tag = 0
            total_cc6 = 0
            total_cc6_account = 0
            total_per_analytical_account = collections.OrderedDict()
            for account, values in accounts_grouped[pc]['accounts'].items():
                if current_tag and current_tag != values['tag']:
                    lines = self.add_total_tag(account_groups_tag, current_tag, lines, pc, accounts_grouped[pc]['code'],
                                               total_cc6_tag)
                if accounts_grouped[pc]['code'][0] == '7':
                    try:
                        total_cc6_account = totals_cc6[account]
                    except KeyError:
                        total_cc6_account = 0

                if current_tag != values['tag']:
                    current_tag = values['tag']
                    total_cc6_tag = 0

                if current_tag not in account_groups_tag:
                    account_groups_tag[current_tag] = collections.OrderedDict()

                columns = []
                show_account = False
                total_per_account = 0

                for analytical_account in analytical_accounts:
                    if analytical_account not in account_groups_tag[values['tag']]:
                        account_groups_tag[current_tag][analytical_account] = 0.00
                    if analytical_account not in total_per_analytical_account:
                        total_per_analytical_account[analytical_account] = 0.00

                    try:
                        if values[analytical_account] != 0:
                            columns.append(
                                round(values[analytical_account], 2))
                            total_per_account += values[analytical_account]
                            total_per_analytical_account[analytical_account] += values[analytical_account]
                        else:
                            columns.append('')
                        account_groups_tag[current_tag][analytical_account] += values[analytical_account]
                        if values[analytical_account] != 0:
                            show_account = True
                    except KeyError:
                        columns.append('')

                if accounts_grouped[pc]['code'][0] == '7':
                    total_cc6_tag += total_cc6_account
                    total_cc6 += total_cc6_account
                    if total_cc6_account:
                        show_account = True

                if show_account:
                    column_account = [{'name': values['name'], 'style': 'text-align:left'}] + \
                                     [{'name': v, 'style': 'margin-left:0;border-right:1px solid #f3f3f3'}
                                      for v in columns] + \
                                     [{'name': round(total_per_account, 2),
                                       'style': 'background-color:#ffffa6'}]
                    if accounts_grouped[pc]['code'][0] == '7':
                        column_account += [{'name': round(total_cc6_account, 2),
                                            'style': 'background-color:#ffffa6'}]
                        column_account += [{'name': round(total_cc6_account + total_per_account, 2),
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

            columns_total = [{'name': ''}] + \
                            [{'name': round(v, 2) if v else '', 'style': 'font-size:13px'} for v in
                             total_per_analytical_account.values()] \
                + [{'name': round(sum(total_per_analytical_account.values()), 2)}]
            if accounts_grouped[pc]['code'][0] == '7':
                columns_total += [{'name': round(sum(totals_cc6.values()), 2)}]
                columns_total += [{'name': round(sum(totals_cc6.values()) +
                                                 sum(total_per_analytical_account.values()), 2)}]
                total_per_analytical_account_cc7.update(
                    collections.Counter(total_per_analytical_account))
                total_all_cc6 += total_cc6
            else:
                total_per_analytical_account_cc6.update(
                    collections.Counter(total_per_analytical_account))

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
                columns_total_cc = [{'name': ''}] + \
                                   [{'name': round(v, 2) if v else '', 'style': 'font-size:13px'} for v in
                                    total_per_analytical_account_cc6.values()] \
                    + [{'name': round(sum(total_per_analytical_account_cc6.values()), 2)}]
                cc_name = "Total CC6"
            elif count_cc7 > 1 and accounts_grouped[pc]['code'] == last_cc7:
                columns_total_cc = [{'name': ''}] + \
                                   [{'name': round(v, 2) if v else '', 'style': 'font-size:13px'} for v in
                                    total_per_analytical_account_cc7.values()] \
                    + [{'name': round(sum(total_per_analytical_account_cc7.values()), 2)},
                       {'name': round(total_all_cc6, 2)},
                       {'name': round(total_all_cc6 +
                                      sum(total_per_analytical_account_cc7.values()), 2)}
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
        total = sum(account_groups_tag[current_tag].values())
        if total != 0 or (pc_code[0] == '7' and total_cc6 != 0):
            additional_columns = 2
            columns = [{'name': current_tag}] + \
                      [{'name': round(total_per_account, 2) if total_per_account != 0 else '',
                        'style': 'text-align:right;font-size:13px'}
                       for total_per_account in account_groups_tag[current_tag].values()] + \
                      [{'name': round(total, 2),
                        'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
            if pc_code[0] == '7':
                columns += [{'name': round(total_cc6, 2),
                             'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
                columns += [{'name': round(total_cc6 + total, 2),
                             'style': 'text-align:right;font-size:12px;background-color:#ffffa6'}]
                additional_columns = 4
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
