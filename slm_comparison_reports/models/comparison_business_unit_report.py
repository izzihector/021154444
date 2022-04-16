# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from dateutil.parser import parse


class ComparisonBusinessUnitReport(models.AbstractModel):
    _name = "comparison.business.unit.report"
    _description = "Comparison Unit Report"
    _inherit = "account.report"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month', 'mode': 'range'}
    filter_comparison = None
    filter_cash_basis = False
    filter_all_entries = False
    filter_hierarchy = False
    filter_unfold_all = None
    filter_multi_company = None
    filter_report_type = None
    filter_profit_center = None
    filter_encription = None
    filter_business_unit = True
    MAX_LINES = None
    columns = 40

    @api.model
    def _get_report_name(self):
        return _("Comparison Business Unit Report")

    def _get_templates(self):
        templates = super(ComparisonBusinessUnitReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''}] * self.columns

    def _get_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = super(ComparisonBusinessUnitReport, self)._get_options(previous_options)
        if options.get('business_unit'):
            business_units = [{'name': 'SACS', 'id': 250}, {'name': 'SCS', 'id': 252}, {'name': 'SGS', 'id': 251}]
            options['business_unit'] = [{'id': c['id'], 'name': c['name'], 'selected': False} for c in business_units]

        # Merge old options with default from this report
        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                if key == 'business_unit':
                    options[key] = previous_options[key]
        return options

    def _set_context(self, options):
        ctx = super(ComparisonBusinessUnitReport, self)._set_context(options)
        business_units = []
        if options.get('business_unit'):
            business_units = [c.get('id') for c in options['business_unit'] if c.get('selected')]
            business_units = business_units if len(business_units) > 0 else [c.get('id')
                                                                             for c in options['business_unit']]
        ctx['business_units'] = len(business_units) > 0 and business_units

        return ctx

    def _do_query(self, options, line_id, limit=False):
        context = dict(self._context or {})

        select_all = """
            SELECT id, profit_center, profit_center_id, name, sequence, formula, sum(balance) as balance, type
                FROM (
        """

        where_args = ['%s' for profit_center in context['business_units']]
        select_expression = """
            WITH accounts_expression AS (
                SELECT DISTINCT expression, AA.id
                FROM business_unit_mapping_line BUML
                JOIN  business_unit_mapping BUM ON (BUML.business_unit_mapping_id = BUM.id)
                JOIN account_account AA ON (AA.code LIKE CONCAT(BUML.expression, %s))
                WHERE BUM.profit_center in ({})
                    AND BUML.expression IS NOT NULL
            )
        """.format(','.join(where_args))

        select_all += select_expression

        select_fields = """
            SELECT
             BUM.name AS profit_center,
             BUM.profit_center AS profit_center_id,
             {}.name,
             BURL.sequence,
             BURL.formula,
             BURL.id,
             SUM(planned_amount * (BEML.encryption / 100) * (CASE WHEN BURL.sign THEN -1 ELSE 1 END)) AS balance,
             BURL.type
        """
        select_fields_group = select_fields.format('BUG')
        select_fields_tag = select_fields.format('BUT')

        common_tables = """
            FROM business_unit_mapping BUM
             JOIN business_unit_mapping_line BUML ON (BUM.id = BUML.business_unit_mapping_id)
             JOIN {} ON BUML.{} = {}.id
             JOIN business_unit_report_layout BURL on (BUM.id = BURL.business_unit_mapping_id AND {}.id = BURL.{})
        """
        common_tables_tag = common_tables.format('business_unit_tag BUT', 'tag', 'BUT', 'BUT', 'tag')
        common_tables_group = common_tables.format('business_unit_group BUG', 'group', 'BUG', 'BUG', 'group')

        account_tables = """
            JOIN account_account AA_ID ON (AA_ID.id = BUML.account_id)
            JOIN account_account AA ON (AA_ID.code = AA.code )
        """

        account_tag_tables = """
            JOIN account_account_account_tag AAAT ON (AAAT.account_account_tag_id = BUML.tag_id)
            JOIN account_account AA ON (AAAT.account_account_id = AA.id)
        """

        account_group_tables = """
            JOIN account_account AA ON (BUML.group_id = AA.group_id)
        """

        account_expression_tables = """
            JOIN accounts_expression ON (accounts_expression.expression = BUML.expression)
            JOIN account_account AA ON (accounts_expression.id = AA.id)
        """

        encryption_tables = """
            JOIN account_budget_rel ABR ON (ABR.account_id = AA.id)
            JOIN account_budget_post ABP ON (ABP.id = ABR.budget_id)
            JOIN crossovered_budget_lines CBL ON (CBL.general_budget_id = ABP.id)
            JOIN budget_encryption_mapping_line BEML ON (BEML.analytical_account_id = CBL.analytic_account_id AND
                                                                BUM.profit_center = BEML.cost_center)
            JOIN budget_encryption_mapping BEM ON (BEML.budget_encryption_mapping_id = BEM.id
                                        AND
                                      TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD') <= CBL.date_from
                                        AND (date_trunc('month',
                                                        TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD')) +
                                             interval '1 month' - interval '1 day') >= CBL.date_to)    
        """

        where_args = ['%s' for profit_center in context['business_units']]
        where = """
            WHERE BUM.profit_center in ({})
                AND CBL.date_from >= %s
                AND CBL.date_to <= %s
                AND BEML.encryption > 0
        """.format(','.join(where_args))

        where_cond_expression = """ AND BUML.expression IS NOT NULL """

        group_by = """
            GROUP BY BUM.name,
               {}.name,
               BURL.sequence,
               BURL.formula,
               BURL.type,
               BUM.profit_center,
               BURL.id
        """

        group_by_tag = group_by.format('BUT')
        group_by_group = group_by.format('BUG')

        select_all_empty = """
           SELECT BUM.name,
                BUM.profit_center as profit_center_id,
               COALESCE(
                             BUT.name,
                             BUG.name,
                             BURL.name
                ) AS name, BURL.sequence, BURL.formula, BURL.id, 0 AS balance,
               BURL.type
          FROM business_unit_mapping BUM
                 JOIN business_unit_mapping_line BUML ON (BUM.id = BUML.business_unit_mapping_id)
                 JOIN business_unit_report_layout BURL ON (BUM.id = BURL.business_unit_mapping_id)
                 LEFT JOIN business_unit_tag BUT ON (BUML.tag = BUT.id AND BURL.tag = BUML.tag)
                 LEFT JOIN business_unit_group BUG ON (BUML.group = BUG.id AND BURL.group = BUML.group)
          WHERE profit_center in ({})
            AND ( 
                BUT.name IS NOT NULL
                OR BUG.name IS NOT NULL
                OR BURL.name IS NOT NULL
                )
          GROUP BY COALESCE(
                     BUT.name,
                     BUG.name,
                     BURL.name
              ),
                   BUM.name,
                   BURL.sequence,
                   BURL.formula,
                   balance,
                   BURL.type,
                   BURL.id,
                   BUM.profit_center
        """.format(','.join(where_args))

        end_select = """
            ) AS A
            GROUP BY profit_center,
                     name,
                     formula,
                     sequence,
                     type,
                     profit_center_id,
                     id
            ORDER BY profit_center, sequence;
        """

        union = """ UNION ALL """

        select_tag_accounts = select_fields_tag + common_tables_tag + account_tables + encryption_tables + where + \
                              group_by_tag
        select_group_accounts = select_fields_group + common_tables_group + account_tables + encryption_tables + \
                                where + group_by_group
        select_tag_account_tag = select_fields_tag + common_tables_tag + account_tag_tables + encryption_tables + \
                                 where + group_by_tag
        select_group_account_tag = select_fields_group + common_tables_group + account_tag_tables + \
                                   encryption_tables + where + group_by_group
        select_tag_account_group = select_fields_tag + common_tables_tag + account_group_tables + encryption_tables \
                                   + where + group_by_tag
        select_group_account_group = select_fields_group + common_tables_group + account_group_tables + encryption_tables \
                                     + where + group_by_group
        select_tag_expression = select_fields_tag + common_tables_tag + account_expression_tables + \
                                encryption_tables + where + where_cond_expression + group_by_tag
        select_group_expression = select_fields_group + common_tables_group + account_expression_tables + \
                                  encryption_tables + where + where_cond_expression + group_by_group

        sql = select_all + select_tag_accounts + union + select_group_accounts + union + select_tag_account_tag + \
              union + select_group_account_tag + union + select_tag_account_group + union + select_group_account_group \
              + union + select_tag_expression + union + select_group_expression + union + select_all_empty + end_select

        params_profit_center = tuple(profit_center for profit_center in context['business_units'])

        params = ('%',) + params_profit_center + \
                 (params_profit_center + (context.get('date_from'), context.get('date_to'))) * 8 + params_profit_center
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _do_query_overhead(self):
        context = dict(self._context or {})

        sql = """
            WITH REPORT AS (SELECT DISTINCT BUM.profit_center AS profit_center_id, BEML.encryption AS overhead, BEM.month, BEM.year
                FROM business_unit_mapping BUM
                       JOIN account_analytic_account AAA_BUM ON (BUM.profit_center = AAA_BUM.id)
                       JOIN account_analytic_account AAA
                         ON (AAA.code = ('7' || Substring(AAA_BUM.code FROM 2 FOR CHAR_LENGTH(AAA_BUM.code) - 1)))
                       JOIN budget_encryption_mapping_line BEML ON (BEML.cost_center = AAA.id)
                       JOIN budget_encryption_mapping BEM ON (BEM.id = BEML.budget_encryption_mapping_id)
                WHERE TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD') >= %s
                  AND (date_trunc('month', TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD')) +
                       interval '1 month' - interval '1 day') <= %s),
                 OVERHEAD_BALANCE AS (SELECT COALESCE(SUM(
                                                        planned_amount * (BEML.encryption / 100)), 0) AS balance,
                                             BEM.month,
                                             BEM.year
                                      FROM budget_encryption_mapping BEM
                                             JOIN budget_encryption_mapping_line BEML
                                               on (BEM.id = BEML.budget_encryption_mapping_id)
                                             JOIN crossovered_budget_lines CBL
                                               ON (CBL.analytic_account_id = BEML.analytical_account_id)
                                      WHERE BEML.cost_center =
                                            (SELECT id FROM account_analytic_account WHERE code LIKE %s
                                                                                       AND name LIKE %s limit 1)
                                        AND CBL.date_from >= %s
                                        AND CBL.date_to <= %s
                                        AND TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD') <= CBL.date_from
                                        AND (date_trunc('month', TO_DATE(CONCAT(BEM.year, BEM.month, '01'), 'YYYYMMDD')) +
                                             interval '1 month' - interval '1 day') >= CBL.date_from
                                      GROUP BY BEM.month, BEM.year)
            SELECT SUM(OVERHEAD_BALANCE.balance * REPORT.overhead / 100) AS balance, profit_center_id
            FROM REPORT
                   JOIN OVERHEAD_BALANCE ON (REPORT.month = OVERHEAD_BALANCE.month AND REPORT.year = OVERHEAD_BALANCE.year)
            GROUP BY profit_center_id;
        """
        params = (context.get('date_from'), context.get('date_to'), '6%', '%OVERHEAD%', context.get('date_from'),
                  context.get('date_to'))
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return {row['profit_center_id']: row['balance'] for row in results}

    def _resolve_formula(self, options, line_id):
        context = dict(self._context or {})
        results = self._do_query(options, line_id)
        overhead = self._do_query_overhead()

        for profit_center_id in context['business_units']:
            results_by_code = {'E{}'.format(result['id']): result['balance'] for result in results
                               if result['profit_center_id'] == profit_center_id}
            results_by_code['result'] = 0
            for i, result in enumerate(results):
                if result['profit_center_id'] == profit_center_id and result['type'] == 'overhead':
                    try:
                        results[i]['balance'] = overhead[profit_center_id]
                        results_by_code['E{}'.format(result['id'])] = overhead[profit_center_id]
                    except KeyError:
                        pass
                if result['profit_center_id'] == profit_center_id and result['type'] == 'total':
                    formula = 'result = {}'.format(re.sub(r"([0-9]+(\.[0-9]+)?)", r"E\1", result['formula']).strip())
                    safe_eval(formula, results_by_code, mode='exec', nocopy=True)
                    results_by_code['E{}'.format(result['id'])] = results_by_code['result']
                    results[i]['balance'] = results_by_code['result']
        return results

    def _get_lines(self, options, line_id=None):
        rows = self._resolve_formula(options, line_id)
        lines = []
        current_pc = ''
        for row in rows:
            if row['profit_center_id'] != current_pc:
                if current_pc:
                    lines.append({
                        'id': 'header empty',
                        'name': '',
                        'title_hover': '',
                        'columns': [],
                        'level': 3,
                        'unfoldable': False,
                        'colspan': 1,
                        'style': ''
                    })
                current_pc = row['profit_center_id']
                lines.append({
                    'id': 'header',
                    'name': row['profit_center'],
                    'title_hover': 'Profit Center',
                    'columns': [],
                    'level': 1,
                    'unfoldable': False,
                    'colspan': 2,
                    'style': 'text-align:center;font-size:14px;background-color:lightblue'
                })
                lines.append({
                    'id': 'analytical_accounts_{}'.format(current_pc),
                    'name': '',
                    'title_hover': row['profit_center'],
                    'columns': [{'name': ''}],
                    'level': 2,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:center;font-size:15px;background-color:#eff5f7'
                })

            if row['type'] == 'group':
                lines.append({
                    'id': row['name'],
                    'name': row['name'],
                    'title_hover': row['name'],
                    'columns': [{'name': round(row['balance'], 2), 'style': 'text-align:right'}],
                    'level': 2,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:left;font-size:14px;background-color:#f2f2f3'
                })
            elif row['type'] == 'total':
                lines.append({
                    'id': row['name'],
                    'name': row['name'],
                    'title_hover': row['name'],
                    'columns': [{'name': round(row['balance'], 2), 'style': 'text-align:right'}],
                    'level': 1,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:left;font-size:14px;background-color:lightblue'
                })
            else:
                lines.append({
                    'id': row['name'],
                    'name': row['name'],
                    'title_hover': row['name'],
                    'columns': [{'name': round(row['balance'], 2), 'style': 'text-align:right'}],
                    'level': 3,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:left;width:10%'
                })
        return lines
