# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime


class AccountLPLReport(models.AbstractModel):
    _name = "account.lpl.report"
    _description = "Layout Profit & Loss Report"
    _inherit = "account.report"

    filter_date = {'date_from': '', 'date_to': '',
                   'filter': 'this_month', 'mode': 'range'}
    filter_comparison = None
    filter_cash_basis = False
    filter_all_entries = False
    filter_hierarchy = False
    filter_unfold_all = None
    filter_multi_company = None
    filter_profit_center_accounts = None
    filter_encryption = None
    filter_tags = True
    filter_subgroups = True
    MAX_LINES = None
    columns = 14

    @api.model
    def _get_report_name(self):
        return _("Layout Profit & Loss Report")

    def _get_templates(self):
        templates = super(AccountLPLReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    # def _get_columns(self, options):
    #     return self.columns

    def _get_columns_name(self, options):
        return [{'name': ''}] * self.columns

    def _set_context(self, options):
        ctx = super(AccountLPLReport, self)._set_context(options)
        tags = []
        if options.get('tags'):
            tags = [tag.get('id')
                    for tag in options['tags'] if tag.get('selected')]
            tags = tags if len(tags) > 0 else []
        ctx['tags'] = len(tags) > 0 and tags

        if options.get('subgroups'):
            ctx['show_subgroups'] = options['subgroups'][0]['selected']

        return ctx

    def _get_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = super(AccountLPLReport, self)._get_options(previous_options)
        if options.get('tags'):
            tags = self._get_tags()
            options['tags'] = [
                {'id': id, 'name': tags[id], 'selected': False} for id in tags]
        if options.get('subgroups'):
            options['subgroups'] = [
                {'id': 1, 'name': 'Yes', 'selected': False}]

        # Merge old options with default from this report
        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                if key in ['tags', 'subgroups']:
                    options[key] = previous_options[key]

        return options

    def _do_query_lpl(self, date_from=None, date_to=None, report_id=1, balance=False):
        context = dict(self._context or {})
        join_groups = """
            JOIN account_group_slm_financial_reports_define_lines_rel AGSFRDLR
               ON (AGSFRDLR.slm_financial_reports_define_lines_id = SFRDL.id AND
                   AGSFRDLR.account_group_id = AA.group_id)
        """
        where_without_groups = """
            AND (SELECT count(*) FROM account_group_slm_financial_reports_define_lines_rel WHERE slm_financial_reports_define_lines_id = SFRDL.id) = 0
        """
        sql_main = """
            SELECT SFRDL.name,
                         balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END) AS balance,
                         SFRDL.type,
                         SFRDL.formula,
                         SFRDL.code,
                         SFRDL.id,
                         SFRDL.sequence,
                         SFRDL.sign
                  FROM slm_financial_reports_define SFRD
                         JOIN slm_financial_reports_define_lines SFRDL ON (SFRD.id = SFRDL.report_id)
                         JOIN account_account_tag_slm_financial_reports_define_lines_rel AATSFRDLR
                           ON (SFRDL.id = AATSFRDLR.slm_financial_reports_define_lines_id)
                         JOIN account_account_account_tag AAAT ON (AAAT.account_account_tag_id = AATSFRDLR.account_account_tag_id)
                         JOIN account_account AA ON (AAAT.account_account_id = AA.id)
                         {1}
                         JOIN account_move_line AML ON (AA.id = AML.account_id)
                         JOIN account_move AM ON (AML.move_id = AM.id)
                         LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                               AND RCR.name = date_trunc('month', AML.date) :: date)
                  WHERE SFRD.id = {0}
                    AND AML.company_id IN (2, 3, 4, 5, 6, 7)
                    AND AML.date <= %s
                    AND AML.date >= %s
                    AND AM.state = %s
                    {2}
        """
        sql_groups = sql_main.format(report_id, join_groups, '')
        sql_without_groups = sql_main.format(
            report_id, '', where_without_groups)
        sql = """
            SELECT name,
                (CASE
                    WHEN TRIM(sign) = '+' THEN ABS(SUM(balance)) 
                    WHEN TRIM(sign) = '-' THEN ABS(SUM(balance)) * -1
                    ELSE SUM(balance) 
                END) AS balance, 
                type, formula, code, id, sign
            FROM (
                  {1}
                  UNION ALL
                  {2}
                  UNION ALL
                  SELECT SFRDL.name, 0 AS balance, SFRDL.type, SFRDL.formula, SFRDL.code, SFRDL.id, SFRDL.sequence,
                        SFRDL.sign
                  FROM slm_financial_reports_define SFRD
                         JOIN slm_financial_reports_define_lines SFRDL ON (SFRD.id = SFRDL.report_id)
            
                  WHERE SFRD.id = {0}) AS A
            
            GROUP BY name, sequence, type, formula, code, id, sign
            ORDER BY sequence
        """.format(report_id, sql_groups, sql_without_groups)
        company = self.env['res.company'].search([('id', '=', 2)], limit=1)
        date_to = context.get('date_to') if date_to is None else date_to
        date_to = parse(date_to).date() if isinstance(
            date_to, str) else date_to

        if balance:
            date_from = datetime.fromtimestamp(0)
        else:
            fiscal_year = company.compute_fiscalyear_dates(date_to)
            date_from = fiscal_year['date_from'] if date_from is None else date_from

        params = (date_to, date_from, 'posted') * 2
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _do_query_lpl_budget(self, date_from=None, date_to=None, report_id=1, balance=False):
        context = dict(self._context or {})
        join_groups = """
                    JOIN account_group_slm_financial_reports_define_lines_rel AGSFRDLR
                       ON (AGSFRDLR.slm_financial_reports_define_lines_id = SFRDL.id AND
                           AGSFRDLR.account_group_id = AA.group_id)
                """
        where_without_groups = """
                    AND (SELECT count(*) FROM account_group_slm_financial_reports_define_lines_rel WHERE slm_financial_reports_define_lines_id = SFRDL.id) = 0
                """
        sql_main = """
                    SELECT SFRDL.name,
                                 planned_amount AS balance,
                                 SFRDL.type,
                                 SFRDL.formula,
                                 SFRDL.code,
                                 SFRDL.id,
                                 SFRDL.sequence,
                                 SFRDL.sign
                          FROM slm_financial_reports_define SFRD
                                 JOIN slm_financial_reports_define_lines SFRDL ON (SFRD.id = SFRDL.report_id)
                                 JOIN account_account_tag_slm_financial_reports_define_lines_rel AATSFRDLR
                                   ON (SFRDL.id = AATSFRDLR.slm_financial_reports_define_lines_id)
                                 JOIN account_account_account_tag AAAT ON (AAAT.account_account_tag_id = AATSFRDLR.account_account_tag_id)
                                 JOIN account_account AA ON (AAAT.account_account_id = AA.id)
                                 {1}
                                 JOIN account_budget_rel ABR ON (ABR.account_id = AAAT.account_account_id)
                                 JOIN account_budget_post ABP ON (ABP.id = ABR.budget_id)
                                 JOIN crossovered_budget_lines CBL ON (CBL.general_budget_id = ABP.id)
                          WHERE SFRD.id = {0}
                            AND CBL.date_to <= %s
                            AND CBL.date_from >= %s
                            {2}
                """
        sql_groups = sql_main.format(report_id, join_groups, '')
        sql_without_groups = sql_main.format(
            report_id, '', where_without_groups)
        sql = """
                    SELECT name,
                        (CASE
                            WHEN TRIM(sign) = '+' THEN ABS(SUM(balance)) 
                            WHEN TRIM(sign) = '-' THEN ABS(SUM(balance)) * -1
                            ELSE SUM(balance) 
                        END) AS balance, 
                        type, formula, code, id, sign
                    FROM (
                          {1}
                          UNION ALL
                          {2}
                          UNION ALL
                          SELECT SFRDL.name, 0 AS balance, SFRDL.type, SFRDL.formula, SFRDL.code, SFRDL.id, SFRDL.sequence,
                                SFRDL.sign
                          FROM slm_financial_reports_define SFRD
                                 JOIN slm_financial_reports_define_lines SFRDL ON (SFRD.id = SFRDL.report_id)

                          WHERE SFRD.id = {0}) AS A

                    GROUP BY name, sequence, type, formula, code, id, sign
                    ORDER BY sequence
                """.format(report_id, sql_groups, sql_without_groups)

        company = self.env['res.company'].search([('id', '=', 2)], limit=1)
        date_to = context.get('date_to') if date_to is None else date_to
        date_to = parse(date_to).date() if isinstance(
            date_to, str) else date_to
        if balance:
            date_from = datetime.fromtimestamp(0)
        else:
            fiscal_year = company.compute_fiscalyear_dates(date_to)
            date_from = fiscal_year['date_from'] if date_from is None else date_from
        params = (date_to, date_from) * 2
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _get_tags(self, report_id=1):

        sql = """
            SELECT AAT.id, AAT.name
            FROM slm_financial_reports_define_lines SFRDL
                   JOIN account_account_tag_slm_financial_reports_define_lines_rel AATSFRDLR
                     ON (SFRDL.id = AATSFRDLR.slm_financial_reports_define_lines_id)
                   JOIN account_account_tag AAT ON (AATSFRDLR.account_account_tag_id = AAT.id)
            WHERE SFRDL.report_id = {}
            ORDER BY SFRDL.sequence;
        """.format(report_id)
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        tags = {}
        for result in results:
            tags[result['id']] = result['name']
        return tags

    def _do_query_lpl_tag(self, tag_id, context, date_from=None, date_to=None, order='DESC', report_id=1,
                          balance=False):
        join_groups = """
                            JOIN account_group_slm_financial_reports_define_lines_rel AGSFRDLR
                               ON (AGSFRDLR.slm_financial_reports_define_lines_id = SFRDL.id AND
                                   AGSFRDLR.account_group_id = AA.group_id)
                        """
        where_without_groups = """
                            AND (SELECT count(*) FROM account_group_slm_financial_reports_define_lines_rel 
                            WHERE slm_financial_reports_define_lines_id = SFRDL.id) = 0
                        """

        select_subgroups = "ASG.name, ASG.id," if context['show_subgroups'] else ''
        join_subgroups = "LEFT JOIN account_subgroup ASG ON (ASG.id = AA.subgroup_id)" if context[
            'show_subgroups'] else ''

        sql_main = """
            SELECT AG.name AS group_name,
                   AG.id AS group_id,
                   {3}
                   SUM(balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)) AS balance
            FROM slm_financial_reports_define_lines SFRDL
                   JOIN account_account_tag_slm_financial_reports_define_lines_rel AATSFRDLR
                     ON (SFRDL.id = AATSFRDLR.slm_financial_reports_define_lines_id )
                   JOIN account_account_account_tag AAAT
                     ON (AAAT.account_account_tag_id = AATSFRDLR.account_account_tag_id)
                   JOIN account_account AA ON (AAAT.account_account_id = AA.id)
                   JOIN account_group AG ON (AA.group_id = AG.id)
                   {4}
                   {1}
                   JOIN account_move_line AML ON (AA.id = AML.account_id)
                   JOIN account_move AM ON (AML.move_id = AM.id)
                   LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                         AND RCR.name = date_trunc('month', AML.date) :: date)
            WHERE SFRDL.report_id = {0}
              AND AAAT.account_account_tag_id = %s
              AND AML.company_id IN (2, 3, 4, 5, 6, 7)
              AND AML.date >= %s
              AND AML.date <= %s
              AND AM.state = %s
              {2}
            GROUP BY {3} AG.name, AG.id

            UNION ALL
            SELECT DISTINCT AG.name AS group_name, AG.id AS group_id, {3} 0 AS balance
            FROM slm_financial_reports_define_lines SFRDL
                   JOIN account_account_tag_slm_financial_reports_define_lines_rel AATSFRDLR
                     ON (SFRDL.id = AATSFRDLR.slm_financial_reports_define_lines_id)
                   JOIN account_account_account_tag AAAT
                     ON (AAAT.account_account_tag_id = AATSFRDLR.account_account_tag_id)
                   JOIN account_account AA ON (AAAT.account_account_id = AA.id)
                   JOIN account_group AG ON (AA.group_id = AG.id)
                   {4}
                   {1}
            WHERE AAAT.account_account_tag_id = %s
            {2}
        """
        sql_groups = sql_main.format(
            report_id, join_groups, '', select_subgroups, join_subgroups)
        sql_without_groups = sql_main.format(report_id, '', where_without_groups,
                                             select_subgroups, join_subgroups)

        group_by_subgroups = "name, id," if context['show_subgroups'] else ''
        sql = """
            SELECT *
            FROM (SELECT {3} group_name, group_id, SUM(balance) as balance
                  FROM (
                    {0}
                    UNION ALL
                    {1}
                    ) AS U
                  GROUP BY {3} group_name, group_id) AS T
            ORDER BY group_name, balance {2}
        """.format(sql_groups, sql_without_groups, order, group_by_subgroups)
        company = self.env['res.company'].search([('id', '=', 2)], limit=1)
        date_to = context.get('date_to') if date_to is None else date_to
        date_to = parse(date_to).date() if isinstance(
            date_to, str) else date_to
        if balance:
            date_from = datetime.fromtimestamp(0)
        else:
            fiscal_year = company.compute_fiscalyear_dates(date_to)
            date_from = fiscal_year['date_from'] if date_from is None else date_from
        params = (tag_id, date_from, date_to, 'posted', tag_id) * 2
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        # Order the results in ascending order if all number are negatives
        # if results and results[-1]['balance'] < 0 and order != 'ASC':
        #     return self._do_query_lpl_tag(tag_id, context, date_from, date_to, 'ASC')
        # else:
        return results

    def _do_query_lpl_budget_tag(self, tag_id, context, date_from=None, date_to=None, order='DESC', report_id=1,
                                 balance=False):
        join_groups = """
                                    JOIN account_group_slm_financial_reports_define_lines_rel AGSFRDLR
                                       ON (AGSFRDLR.slm_financial_reports_define_lines_id = SFRDL.id AND
                                           AGSFRDLR.account_group_id = AA.group_id)
                                """
        where_without_groups = """
                                    AND (SELECT count(*) FROM account_group_slm_financial_reports_define_lines_rel 
                                    WHERE slm_financial_reports_define_lines_id = SFRDL.id) = 0
                                """
        select_subgroups = "ASG.name, ASG.id," if context['show_subgroups'] else ''
        join_subgroups = "LEFT JOIN account_subgroup ASG ON (ASG.id = AA.subgroup_id)" if context[
            'show_subgroups'] else ''

        sql_main = """
            SELECT AG.name AS group_name, AG.id AS group_id, {3} SUM(planned_amount) AS balance
                            FROM slm_financial_reports_define_lines SFRDL
                                   JOIN account_account_tag_slm_financial_reports_define_lines_rel AATSFRDLR
                                     ON (SFRDL.id = AATSFRDLR.slm_financial_reports_define_lines_id)
                                   JOIN account_account_account_tag AAAT
                                     ON (AAAT.account_account_tag_id = AATSFRDLR.account_account_tag_id)
                                   JOIN account_account AA ON (AAAT.account_account_id = AA.id)
                                   JOIN account_group AG ON (AA.group_id = AG.id)
                                   {4}
                                   {1}
                                   JOIN account_budget_rel ABR ON (ABR.account_id = AA.id)
                                   JOIN account_budget_post ABP ON (ABP.id = ABR.budget_id)
                                   JOIN crossovered_budget_lines CBL ON (CBL.general_budget_id = ABP.id)
                            WHERE SFRDL.report_id = {0}
                              AND AAAT.account_account_tag_id = %s
                              AND CBL.date_from >= %s
                              AND CBL.date_to <= %s
                              {2}
                            GROUP BY {3} AG.name, AG.id
                            
                            UNION ALL
                            SELECT DISTINCT AG.name AS group_name, AG.id AS group_id, {3} 0 AS balance
                            FROM slm_financial_reports_define_lines SFRDL
                                   JOIN account_account_tag_slm_financial_reports_define_lines_rel AATSFRDLR
                                     ON (SFRDL.id = AATSFRDLR.slm_financial_reports_define_lines_id)
                                   JOIN account_account_account_tag AAAT
                                     ON (AAAT.account_account_tag_id = AATSFRDLR.account_account_tag_id)
                                   JOIN account_account AA ON (AAAT.account_account_id = AA.id)
                                   JOIN account_group AG ON (AA.group_id = AG.id)
                                   {4}
                                   {1}
                            WHERE AAAT.account_account_tag_id = %s
                            {2}
        """
        sql_groups = sql_main.format(
            report_id, join_groups, '', select_subgroups, join_subgroups)
        sql_without_groups = sql_main.format(report_id, '', where_without_groups, select_subgroups,
                                             join_subgroups)

        group_by_subgroups = "name, id," if context['show_subgroups'] else ''
        sql = """
                SELECT *
                FROM (SELECT {3} group_name, SUM(balance) as balance
                      FROM (
                      {0}
                      UNION ALL
                      {1}
                      ) AS U
                      GROUP BY {3} group_name) AS O
                ORDER BY group_name, balance {2}
           """.format(sql_groups, sql_without_groups, order, group_by_subgroups)

        company = self.env['res.company'].search([('id', '=', 2)], limit=1)
        date_to = context.get('date_to') if date_to is None else date_to
        date_to = parse(date_to).date() if isinstance(
            date_to, str) else date_to
        if balance:
            date_from = datetime.fromtimestamp(0)
        else:
            fiscal_year = company.compute_fiscalyear_dates(date_to)
            date_from = fiscal_year['date_from'] if date_from is None else date_from
        params = (tag_id, date_from, date_to, tag_id) * 2
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        if results and results[-1]['balance'] < 0 and order != 'ASC':
            return self._do_query_lpl_budget_tag(tag_id, context, date_from, date_to, 'ASC')
        else:
            return results

    def _get_layout_results(self, date_from=None, date_to=None, budget=False):
        if budget:
            results = self._do_query_lpl_budget(date_from, date_to)
        else:
            results = self._do_query_lpl(date_from, date_to)
        results_by_code = {result['code']: result['balance']
                           for result in results}
        results_by_code['result'] = 0
        results_by_code['self'] = self
        results_by_code['budget'] = budget
        results_by_code['date_to'] = date_to
        for i, result in enumerate(results):
            if result['type'] == 'tittle' and result['formula']:
                safe_eval(result['formula'], results_by_code,
                          mode='exec', nocopy=True)
                if result['sign'] == '+':
                    results_by_code[result['code']] = abs(
                        results_by_code['result'])
                    results[i]['balance'] = abs(results_by_code['result'])
                else:
                    results_by_code[result['code']] = results_by_code['result']
                    results[i]['balance'] = results_by_code['result']
            elif result['type'] == 'tittle':
                results[i]['type'] = 'header'
        return results

    def _get_lines(self, options, line_id=None):
        lines = []
        context = dict(self._context or {})
        if options.get('date') and options['date'].get('date_from'):
            context['date_from'] = options['date']['date_from']
        if options.get('date'):
            context['date_to'] = options['date'].get(
                'date_to') or options['date'].get('date')
        date_to = parse(context.get('date_to'))
        last_day_last_month = (
            date_to + relativedelta(months=-1) + relativedelta(day=31)).date()
        first_day_last_month = (
            date_to + relativedelta(months=-1)).replace(day=1).date()
        date_last_year = date_to + relativedelta(years=-1)

        lines.append({
            'id': 'header_1',
            'name': '',
            'title_hover': '',
            'columns': [
                           {'name': v, 'style': 'text-align:right;font-size:15px;background-color:lightblue',
                            'colspan': 1}
                           for v in [date_to.strftime('%b %Y'), '', date_to.strftime('%b %Y'), '',
                                     date_last_year.strftime('%b %Y'), '',
                                     last_day_last_month.strftime('%b %Y'), '']]
            + [{'name': v, 'style': 'text-align:center;font-size:15px;background-color:lightblue',
                           'colspan': 1}
               for v in
               ['Afwijking', 'Afwijking Tov', 'Afwijking Tov']],
            'level': 1,
            'unfoldable': False,
            'colspan': 2,
            'style': 'text-align:left;font-size:15px;background-color:lightblue;border-bottom:none',
            'class': 'lpl_sticky_header'
        })
        lines.append({
            'id': 'header_2',
            'name': '',
            'title_hover': '',
            'columns': [{'name': v, 'style': 'text-align:right;font-size:15px;background-color:lightblue;width:10%',
                         'colspan': 1}
                        for v in
                        ['Realisatie', '', 'Begroting', '', 'Realisatie', '', 'Realisatie', '']]
            + [{'name': v, 'style': 'text-align:center;font-size:15px;background-color:lightblue;width:10%',
                           'colspan': 1}
               for v in
               ['Tov Begroting', 'Realisatie Vorig Jaar', 'Realisatie Vorig Maand']],
            'level': 1,
            'unfoldable': False,
            'colspan': 2,
            'style': 'text-align:left;font-size:15px;background-color:lightblue',
            'class': 'lpl_sticky_header'
        })
        lines.append({
            'id': 'header_3',
            'name': 'Descriptions',
            'title_hover': '',
            'columns': [{'name': v, 'style': 'text-align:right;font-size:15px;background-color:#eff5f7'}
                        for v in ['USD', '%', 'USD', '%', 'USD', '%', 'USD', '%', 'USD', 'USD', 'USD']],
            'level': 2,
            'unfoldable': False,
            'colspan': 2,
            'style': 'text-align:left;font-size:15px;background-color:#eff5f7',
            'class': 'lpl_sticky_header'
        })
        tags = []
        if options.get('tags'):
            tags = [tag.get('id')
                    for tag in options['tags'] if tag.get('selected')]
            tags = tags if len(tags) > 0 else []
        context['tags'] = len(tags) > 0 and tags
        if context['tags']:
            lines = self._get_lines_lpl_notes(
                lines, context, last_day_last_month, date_last_year)
        else:
            lines = self._get_lines_lpl(
                lines, last_day_last_month, date_last_year)
        return lines

    def _get_lines_lpl(self, lines, last_day_last_month, date_last_year, use_total=False):
        results = self._get_layout_results()
        results_last_month = self._get_layout_results(
            date_to=last_day_last_month)
        results_last_year = self._get_layout_results(date_to=date_last_year)
        results_budget = self._get_layout_results(budget=True)
        # results_budget_last_month = self._get_lpl_results(date_to=last_day_last_month, budget=True)
        # results_budget_month = self._get_lpl_results(date_from=first_day_last_month, date_to=last_day_last_month,
        #                                              budget=True)

        total = None
        total_budget = None
        total_last_month = None
        total_last_year = None
        for i, result in enumerate(results):
            if result['type'] != 'header':
                if not total:
                    if use_total:
                        total = results[-1]['balance']
                    else:
                        total = result['balance']
                if not total_budget:
                    if use_total:
                        total_budget = results_budget[-1]['balance']
                    else:
                        total_budget = results_budget[i]['balance']
                if not total_last_month:
                    if use_total:
                        total_last_month = results_last_month[-1]['balance']
                    else:
                        total_last_month = results_last_month[i]['balance']
                if not total_last_year:
                    if use_total:
                        total_last_year = results_last_year[-1]['balance']
                    else:
                        total_last_year = results_last_year[i]['balance']
                lines.append({
                    'id': result['id'],
                    'name': result['name'],
                    'title_hover': result['name'],
                    'columns': [{'name': v, 'style': 'text-align:right'}
                                for v in [round(result['balance'], 2),
                                          self._get_percentage(
                                              result['balance'], total),
                                          round(
                                              results_budget[i]['balance'], 2),
                                          self._get_percentage(
                                              results_budget[i]['balance'], total_budget),
                                          round(
                                              results_last_year[i]['balance'], 2),
                                          self._get_percentage(
                                              results_last_year[i]['balance'], total_last_year),
                                          round(
                                              results_last_month[i]['balance'], 2),
                                          self._get_percentage(
                                              results_last_month[i]['balance'], total_last_month),
                                          round(
                                              result['balance'] - results_budget[i]['balance'], 2),
                                          round(
                                              results[i]['balance'] - results_last_year[i]['balance'], 2),
                                          round(results[i]['balance'] - results_last_month[i]['balance'], 2)]],
                    'level': 2,
                    'unfoldable': False,
                    'colspan': 2,
                    'style': 'text-align: left;' + 'font-weight:normal' if result['type'] == 'detail' else ''
                })
            if result['type'] == 'header':
                lines.append({
                    'id': str(result['id']) + '_header',
                    'name': result['name'],
                    'title_hover': '',
                    'columns': [{'name': ''} for i in range(self.columns - 3)],
                    'level': 2,
                    'unfoldable': False,
                    'colspan': 2,
                    'style': 'text-align: left'
                })

            if result['type'] == 'tittle':
                lines.append({
                    'id': str(result['id']) + '_empty_line',
                    'name': '',
                    'title_hover': '',
                    'columns': [{'name': ''} for i in range(self.columns - 3)],
                    'level': 2,
                    'unfoldable': False,
                    'colspan': 2,
                    'style': 'text-align: left;' + 'font-weight:normal' if result['type'] == 'detail' else ''
                })

        return lines

    def _get_lines_lpl_notes(self, lines, context, last_day_last_month, date_last_year):
        show_subgroups = context['show_subgroups']
        for tag in context['tags']:
            results = self._do_query_lpl_tag(tag, context)
            if results and results[0]['balance'] < 0:
                order = 'ASC'
            else:
                order = 'DESC'
            results_last_month = self._do_query_lpl_tag(
                tag, context, date_to=last_day_last_month, order=order)
            results_last_year = self._do_query_lpl_tag(
                tag, context, date_to=date_last_year, order=order)
            results_budget = self._do_query_lpl_budget_tag(
                tag, context, order=order)
            name = self._get_tags()[tag]

            lines.append({
                'id': str(tag),
                'name': name,
                'title_hover': '',
                'columns': [{'name': ''} for i in range(self.columns - 3)],
                'level': 2,
                'unfoldable': False,
                'colspan': 2,
                'style': 'text-align: left;font-size:15px'
            })

            total = []
            total_tag = [0, 0, 0, 0]
            total_group = [0, 0, 0, 0]
            total = [0, 0, 0, 0]
            current_group = None
            # CHeck if this tag has subgroups

            if results:
                total = [results[0]['balance'], results_budget[0]['balance'], results_last_year[0]['balance'],
                         results_last_month[0]['balance']]
            for i, result in enumerate(results):
                total_tag = [x + y for x, y in zip(total_tag, [result['balance'], results_budget[i]['balance'],
                                                               results_last_year[i]['balance'],
                                                               results_last_month[i]['balance']])]

            style_subheader = 'text-align: left;font-size:14px;font-weight:600'
            subgroups = show_subgroups
            for i, result in enumerate(results):
                if result['group_name'] != current_group:
                    if subgroups:
                        self.add_subtotal_group(
                            current_group, lines, style_subheader, total_group, total_tag)
                    subgroups = 'name' in result and bool(
                        result['name']) and show_subgroups
                    if subgroups:
                        total_group = [0, 0, 0, 0]
                        current_group = result['group_name']
                        lines.append({
                            'id': str(current_group),
                            'name': current_group,
                            'title_hover': '',
                            'columns': [{'name': ''} for i in range(self.columns - 3)],
                            'level': 3,
                            'unfoldable': False,
                            'colspan': 2,
                            'style': style_subheader
                        })
                total_group = [x + y for x, y in zip(total_group, [result['balance'], results_budget[i]['balance'],
                                                                   results_last_year[i]['balance'],
                                                                   results_last_month[i]['balance']])]

                style_row = style_subheader if not subgroups else 'text-align: left;font-weight:500;text-indent:10px'

                if subgroups:
                    if result['name']:
                        row_name = result['name']
                    else:
                        if result['balance'] != 0:
                            row_name = 'Without subgroup'
                        else:
                            row_name = None
                else:
                    row_name = result['group_name']
                if row_name:
                    lines.append({
                        'id': result['id'] if 'id' in result else result['group_id'],
                        'name': row_name,
                        'title_hover': result['name'] if subgroups else result['group_name'],
                        'columns': [{'name': v, 'style': 'text-align:right;text-indent:0;font-weight:normal'}
                                    for v in [round(result['balance'], 2),
                                              self._get_percentage(
                                                  result['balance'], total_tag[0]),
                                              round(
                                                  results_budget[i]['balance'], 2),
                                              self._get_percentage(
                                                  results_budget[i]['balance'], total_tag[1]),
                                              round(
                                                  results_last_year[i]['balance'], 2),
                                              self._get_percentage(
                                                  results_last_year[i]['balance'], total_tag[2]),
                                              round(
                                                  results_last_month[i]['balance'], 2),
                                              self._get_percentage(
                                                  results_last_month[i]['balance'], total_tag[3]),
                                              round(
                                                  result['balance'] - results_budget[i]['balance'], 2),
                                              round(
                                                  result['balance'] - results_last_year[i]['balance'], 2),
                                              round(result['balance'] - results_last_month[i]['balance'], 2)]],
                        'level': 3,
                        'unfoldable': False,
                        'colspan': 2,
                        'style': style_row
                    })
            if subgroups:
                self.add_subtotal_group(
                    current_group, lines, style_subheader, total_group, total_tag)

            lines.append({
                'id': 'total_' + str(tag),
                'name': 'Totaal ' + name,
                'title_hover': '',
                'columns': [{'name': v, 'style': 'text-align:right'} for v in
                            [round(total_tag[0], 2), 100.00, round(total_tag[1], 2), 100.00,
                             round(total_tag[2], 2), 100.00,
                             round(total_tag[3], 2), 100.00, round(
                                 total_tag[0] - total_tag[1], 2),
                             round(total_tag[0] - total_tag[2], 2),
                             round(total_tag[0] - total_tag[3], 2)]],
                'level': 2,
                'unfoldable': False,
                'colspan': 2,
                'style': 'text-align:left;font-size:14px',
            })

            lines.append({
                'id': str(tag),
                'name': '',
                'title_hover': '',
                'columns': [{'name': ''} for i in range(self.columns - 3)],
                'level': 3,
                'unfoldable': False,
                'colspan': 2,
                'style': 'text-align:left',
            })

        return lines

    def add_subtotal_group(self, current_group, lines, style_subheader, total_group, total_tag):
        if current_group:
            lines.append({
                'id': str(current_group),
                'name': 'Subtotal ' + str(current_group),
                'title_hover': '',
                'columns': [{'name': v, 'style': 'text-align:right'} for v in
                            [round(total_group[0], 2), round(self._get_percentage(total_group[0], total_tag[0]), 2),
                             round(total_group[1], 2), round(
                                 self._get_percentage(total_group[1], total_tag[1]), 2),
                             round(total_group[2], 2), round(
                                 self._get_percentage(total_group[2], total_tag[2]), 2),
                             round(total_group[3], 2), round(
                                 self._get_percentage(total_group[3], total_tag[3]), 2),
                             round(total_group[0] - total_group[1], 2), 0,
                             round(total_group[0] - total_group[3], 2)]],
                'level': 3,
                'unfoldable': False,
                'colspan': 2,
                'style': style_subheader
            })

            lines.append({
                'id': str(current_group),
                'name': '',
                'title_hover': '',
                'columns': [{'name': ''} for i in range(self.columns - 3)],
                'level': 3,
                'unfoldable': False,
                'colspan': 2,
                'style': style_subheader
            })

    def _get_percentage(self, total, value):
        percentage = 0.00
        if value != 0:
            percentage = round(total * 100 / value, 2)

        return percentage
