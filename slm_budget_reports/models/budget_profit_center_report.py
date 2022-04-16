# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from dateutil.parser import parse


class BudgetProfitCenterReport(models.AbstractModel):
    _name = "budget.profit.center.report"
    _description = "Budget Profit Center Report"
    _inherit = "account.report"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month', 'mode': 'range'}
    filter_comparison = None
    filter_cash_basis = False
    filter_all_entries = False
    filter_hierarchy = False
    filter_unfold_all = None
    filter_multi_company = None
    filter_profit_center = True
    filter_encription = None
    MAX_LINES = None
    columns = 80

    @api.model
    def _get_report_name(self):
        return _("Budget Profit Center Report")

    def _get_templates(self):
        templates = super(BudgetProfitCenterReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''}] * self.columns

    def _set_context(self, options):
        ctx = super(BudgetProfitCenterReport, self)._set_context(options)
        profit_centers = []
        if options.get('profit_center'):
            profit_centers = [c.get('id') for c in options['profit_center'] if c.get('selected')]
            profit_centers = profit_centers if len(profit_centers) > 0 else [c.get('id')
                                                                             for c in options['profit_center']]
        ctx['profit_centers'] = len(profit_centers) > 0 and profit_centers

        report_type = []
        if options.get('report_type'):
            report_type = [c.get('id') for c in options['report_type'] if c.get('selected')]
            report_type = report_type if len(report_type) > 0 else [c.get('id')
                                                                    for c in options['report_type']]
        ctx['report_type'] = len(report_type) > 0 and report_type

        return ctx

    def _get_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = super(BudgetProfitCenterReport, self)._get_options(previous_options)
        if options.get('profit_center'):
            reports = self.env['profit.center.report'].search([('profit_center_mapping_id', '=', 1)])
            options['profit_center'] = [{'id': c.id, 'name': c.name.name, 'selected': False} for c in reports]

        if options.get('profit_center'):
            report_types = [{'name': 'Profit Center Report', 'id': 1}, {'name': 'Profit Center Break Report', 'id': 2}]
            options['report_type'] = [{'id': c['id'], 'name': c['name'], 'selected': False} for c in report_types]

        # Merge old options with default from this report
        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                if key in ['profit_center', 'report_type']:
                    options[key] = previous_options[key]
        return options

    def _do_query(self, options, line_id, limit=False):
        context = dict(self._context or {})

        select_all = """
            SELECT sequence, name, type, formula, id, array_agg(profit_center) as profit_center, 
                array_agg(balance) as balance
            FROM (
                SELECT sequence, profit_center, name, sum(balance) as balance, type, formula, id
                FROM (
        """
        select_fields = """
            SELECT PCR.id AS profit_center,
                PCRL.sequence, PCRL.type, PCRL.formula,
                {},
                COALESCE(
                    CASE
                    WHEN PCRL.sign
                        THEN -1 * (SUM(
                                planned_amount * (BEML.encryption / 100)
                        )) * (CASE WHEN PCMLPV.value > 0 THEN PCMLPV.value/100 ELSE 1 END)
                    ELSE SUM(
                                planned_amount * (BEML.encryption / 100)
                        ) * (CASE WHEN PCMLPV.value > 0 THEN PCMLPV.value/100 ELSE 1 END)
                    END,
                    0
                ) AS balance,
                PCRL.id
        """
        select_fields_group = select_fields.format('PCG.name')
        select_fields_tag = select_fields.format('PCT.name')

        common_tables = """
        FROM profit_center_mapping PCM
                  JOIN profit_center_mapping_line PCML ON (PCM.id = PCML.profit_center_mapping_id)
                  JOIN {}
                  JOIN profit_center_report_layout PCRL ON ({})
                  JOIN profit_center_report PCR ON (PCR.profit_center_mapping_id = PCM.id)
                  LEFT JOIN profit_center_mapping_line_partial_value PCMLPV ON 
                        (PCMLPV.profit_center_mapping_line_id = PCML.id AND PCMLPV.report = PCR.id)
        """
        common_tables_group = common_tables.format('profit_center_group PCG ON (PCML.group = PCG.id)',
                                                   'PCRL.group = PCML.group')
        common_tables_tag = common_tables.format('profit_center_tag PCT ON (PCML.tag = PCT.id)', 'PCRL.tag = PCML.tag')

        join_accounts = """
                  JOIN account_account AA ON (AA.id = PCML.account_id)
                  JOIN account_account AA_CODE ON (AA.code = AA_CODE.code )
                  JOIN account_budget_rel ABR ON (ABR.account_id = AA_CODE.id)
                  JOIN account_budget_post ABP ON (ABP.id = ABR.budget_id)
                  JOIN crossovered_budget_lines CBL ON (CBL.general_budget_id = ABP.id)
        """

        join_analytical_accounts = """
                    JOIN account_analytic_account AAA ON (AAA.id = PCML.analytical_account_id)
                    JOIN crossovered_budget_lines CBL ON (CBL.analytic_account_id = AAA.id)
                    JOIN account_budget_post ABP ON (ABP.id = CBL.general_budget_id)
                    JOIN account_budget_rel ABR ON (ABR.budget_id = ABP.id)
                    JOIN account_account AA_CODE ON (AA_CODE.id = ABR.account_id)                    
        """

        join_encryption = """
                    JOIN budget_encryption_mapping_line BEML ON (BEML.analytical_account_id = CBL.analytic_account_id AND
                                                                PCR.profit_center = BEML.cost_center)
                    JOIN budget_encryption_mapping BEM ON (BEML.budget_encryption_mapping_id = BEM.id
                                                AND
                                              TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD') <= CBL.date_from
                                                AND (date_trunc('month',
                                                                TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD')) +
                                                     interval '1 month' - interval '1 day') >= CBL.date_to)    
        """

        where_args = ['%s' for profit_center_id in context['profit_centers']]
        where = """
            WHERE PCM.id = 1
                AND PCR.id in ({})
                AND AA_CODE.id NOT IN (SELECT account_account_id FROM account_account_account_tag 
                    WHERE account_account_tag_id = PCML.excluded_account_tag)
                AND CBL.date_from >= %s
                AND CBL.date_to <= %s
                AND BEML.encryption > 0
        """.format(','.join(where_args))
        group_by = """
            GROUP BY 
                  PCRL.sequence,
                  {},
                  PCRL.sign,
                  PCRL.type,
                  PCRL.formula,
                  PCRL.id,
                  PCR.id,
                  PCMLPV.value
        """
        group_by_group = group_by.format('PCG.name')
        group_by_tag = group_by.format('PCT.name')

        union = """ UNION ALL """

        end_select = """
                 ) AS A
                GROUP BY profit_center, sequence, name, type, formula, id
                ORDER BY sequence, profit_center
            ) AS B
            GROUP BY sequence, name, type, formula, id
        """

        sql_groups_accounts = select_fields_group + common_tables_group + join_accounts + \
                              join_encryption + where + group_by_group

        sql_groups_analytical_accounts = select_fields_group + common_tables_group + join_analytical_accounts + \
                                         join_encryption + where + group_by_group

        sql_tags_accounts = select_fields_tag + common_tables_tag + join_accounts + \
                            join_encryption + where + group_by_tag

        sql_tags_analytical_accounts = select_fields_tag + common_tables_tag + join_analytical_accounts + \
                                       join_encryption + where + group_by_tag

        sql_title_total = """
            SELECT PCR.id AS profit_center, 
                    PCRL.sequence,
                    PCRL.type,
                    PCRL.formula,
                    COALESCE(
                         PCRL.name,
                         PCG.name,
                         PCT.name
                       ),
                    0 as balance,
                    PCRL.id
             FROM profit_center_mapping PCM
                      JOIN profit_center_report_layout PCRL ON (PCM.id = PCRL.profit_center_mapping_id)
                      JOIN profit_center_report PCR ON (PCR.profit_center_mapping_id = PCM.id)
                      LEFT JOIN profit_center_group PCG ON (PCRL.group = PCG.id)
                      LEFT JOIN profit_center_tag PCT ON (PCRL.tag = PCT.id)
             WHERE
               PCM.id = 1
               AND PCR.id in ({})
             GROUP BY 
                      PCRL.sequence,
                      PCRL.name,
                      PCG.name,
                      PCT.name,
                      PCRL.type,
                      PCRL.formula,
                      PCRL.id,
                      PCR.id
        """.format(','.join(where_args))

        sql = select_all + sql_groups_accounts + union + sql_groups_analytical_accounts + union + sql_tags_accounts + \
              union + sql_tags_analytical_accounts + union + sql_title_total + end_select
        params_profit_center = tuple(profit_center_id for profit_center_id in context['profit_centers'])
        params = (params_profit_center + (context.get('date_from'), context.get('date_to'))) * 4 + \
                 params_profit_center
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _do_query_overhead(self, profit_center_id):
        sql = """
              WITH REPORT AS (
               SELECT DISTINCT PCR.id, BEML.encryption AS overhead, BEM.month, BEM.year
                       FROM profit_center_report PCR
                              JOIN account_analytic_account AAA_PCR ON (PCR.profit_center = AAA_PCR.id)
                              JOIN account_analytic_account AAA
                                ON (AAA.code = ('7' || Substring(AAA_PCR.code FROM 2 FOR CHAR_LENGTH(AAA_PCR.code) - 1)))
                              JOIN budget_encryption_mapping_line BEML ON (BEML.cost_center = AAA.id)
                              JOIN budget_encryption_mapping BEM ON (BEM.id = BEML.budget_encryption_mapping_id)
                       WHERE TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD') >= %s
                         AND (date_trunc('month', TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD')) +
                              interval '1 month' - interval '1 day') <= %s
                        AND PCR.id = %s),
             OVERHEAD_BALANCE AS (
                 SELECT SUM(planned_amount * (BEML.encryption / 100)) AS balance, BEM.month, BEM.year
                  FROM budget_encryption_mapping BEM
                          JOIN budget_encryption_mapping_line BEML on (BEM.id = BEML.budget_encryption_mapping_id)
                          JOIN crossovered_budget_lines CBL ON (CBL.analytic_account_id = BEML.analytical_account_id
                                                                  AND
                                                                TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD') <= CBL.date_from
                                                                  AND (date_trunc('month',
                                                                                  TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD')) +
                                                                       interval '1 month' - interval '1 day') >=
                                                                      CBL.date_to)
                 WHERE BEML.cost_center =
                       (SELECT id FROM account_analytic_account
                        WHERE code LIKE %s AND name LIKE %s limit 1)
                      AND CBL.date_from >= %s
                      AND CBL.date_to <= %s
                      AND BEML.encryption > 0
                     GROUP BY BEM.month, BEM.year
             )
            SELECT REPORT.overhead, SUM(OVERHEAD_BALANCE.balance * REPORT.overhead / 100) AS balance
           FROM REPORT
                    JOIN OVERHEAD_BALANCE ON (REPORT.month = OVERHEAD_BALANCE.month AND REPORT.year = OVERHEAD_BALANCE.year)
            GROUP BY REPORT.overhead
        """
        context = dict(self._context or {})
        params = context.get('date_from'), context.get('date_to'), profit_center_id, '6%', '%OVERHEAD%', \
                 context.get('date_from'), context.get('date_to')
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _resolve_formula(self, options, line_id=None):
        context = dict(self._context or {})
        results = self._do_query(options, line_id)
        for ipc, profit_center in enumerate(context['profit_centers']):
            results_by_code = {'E{}'.format(result['id']): result['balance'][ipc] for result in results}
            results_by_code['result'] = 0
            overhead = self._get_overhead(profit_center)
            for i, result in enumerate(results):
                if result['type'] == 'overhead':
                    results[i]['balance'][ipc] = overhead['balance']
                    results[i]['name'] = '{} ({}%)'.format(results[i]['name'], overhead['overhead'])
                    results_by_code['E{}'.format(results[i]['id'])] = overhead['balance']
                if result['type'] == 'total':
                    formula = 'result = {}'.format(re.sub(r"([0-9]+(\.[0-9]+)?)", r"E\1", result['formula']).strip())
                    try:
                        safe_eval(formula, results_by_code, mode='exec', nocopy=True)
                    except:
                        pass
                    results_by_code['E{}'.format(result['id'])] = results_by_code['result']
                    results[i]['balance'][ipc] = results_by_code['result']
        return results

    def _get_overhead(self, profit_center_id):
        results = self._do_query_overhead(profit_center_id)
        if results:
            return results[0]
        else:
            return {'overhead': 0, 'balance': 0}

    def _get_lines(self, options, line_id=None):
        lines = []
        grouped_accounts = self._resolve_formula(options, line_id)
        context = dict(self._context or {})
        profit_centers = self.env['profit.center'].browse(context['profit_centers'])
        lines.append({
            'id': 'header',
            'name': profit_centers[0].name.upper() if len(profit_centers) == 1 else '',
            'title_hover': 'Profit Center',
            'columns': ([{'name': v.name.upper(), 'style': 'text-align:right'}
                        for v in profit_centers] if len(profit_centers) > 1 else []) + [{}],
            'level': 1,
            'unfoldable': False,
            'colspan': 2 if len(profit_centers) == 1 else 1,
            'style': 'text-align:left;font-size:14px;background-color:lightblue'
        })

        lines.append({
            'id': 'header_date',
            'name': (parse(context.get('date_from')).strftime("(%B %Y T/M ") +
                     parse(context.get('date_to')).strftime("%B %Y) ")).upper(),
            'title_hover': '',
            'columns': [{'name': v.name + ' TOTAL'} for v in profit_centers] + [{'name': 'TOTAL'}],
            'level': 1,
            'unfoldable': False,
            'colspan': 1,
            'style': 'font-size:14px;background-color:lightblue;text-align:right'
        })

        for grouped_account in grouped_accounts:
            if grouped_account['type'] == 'group':
                lines.append({
                    'id': grouped_account['sequence'],
                    'name': grouped_account['name'],
                    'title_hover': grouped_account['name'],
                    'columns': [
                        {'name':
                             round(balance, 2) if balance else None,
                         'style': 'text-align:right'} for balance in grouped_account['balance']] +
                               [{'name': round(sum(grouped_account['balance']), 2), 'style': 'text-align:right'}],
                    'level': 3,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:left;font-size:14px'
                })
            elif grouped_account['type'] in ('tag', 'overhead'):
                lines.append({
                    'id': grouped_account['sequence'],
                    'name': grouped_account['name'],
                    'title_hover': grouped_account['name'],
                    'columns': [
                        {'name':
                             round(balance, 2) if balance else None,
                         'style': 'text-align:right'} for balance in grouped_account['balance']] +
                               [{'name': round(sum(grouped_account['balance']), 2), 'style': 'text-align:right'}],
                    'level': 1,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:left;font-size:14px;background-color:#f2f2f3'
                })
            elif grouped_account['type'] == 'tittle':
                lines.append({
                    'id': grouped_account['sequence'],
                    'name': grouped_account['name'],
                    'title_hover': grouped_account['name'],
                    'columns': [{'name': ''} for v in profit_centers] + [{}],
                    'level': 2,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:left;font-size:14px;font-weight:bold'
                })
            elif grouped_account['type'] == 'total':
                lines.append({
                    'id': grouped_account['sequence'],
                    'name': grouped_account['name'],
                    'title_hover': grouped_account['name'],
                    'columns': [
                        {'name':
                             round(balance, 2) if balance else None,
                         'style': 'text-align:right'} for balance in grouped_account['balance']] +
                               [{'name': round(sum(grouped_account['balance']), 2), 'style': 'text-align:right'}],
                    'level': 1,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:left;font-size:14px;background-color:lightblue'
                })
        return lines
