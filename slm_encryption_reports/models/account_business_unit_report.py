# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from dateutil.parser import parse


class AccountBusinessUnitReport(models.AbstractModel):
    _name = "account.business.unit.report"
    _description = "Business Unit Report"
    _inherit = "account.report"

    filter_date = {'date_from': '', 'date_to': '',
                   'filter': 'this_month', 'mode': 'range'}
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
        return _("Business Unit Report")

    def _get_templates(self):
        templates = super(AccountBusinessUnitReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''}] * self.columns

    def _get_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = super(AccountBusinessUnitReport,
                        self)._get_options(previous_options)
        if options.get('business_unit'):
            business_units = [{'name': 'SACS', 'id': 250}, {
                'name': 'SCS', 'id': 252}, {'name': 'SGS', 'id': 251}]
            options['business_unit'] = [
                {'id': c['id'], 'name': c['name'], 'selected': False} for c in business_units]

        # Merge old options with default from this report
        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                if key == 'business_unit':
                    options[key] = previous_options[key]
        return options

    def _set_context(self, options):
        ctx = super(AccountBusinessUnitReport, self)._set_context(options)
        business_units = []
        if options.get('business_unit'):
            business_units = [
                c.get('id') for c in options['business_unit'] if c.get('selected')]
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
        business_units = []
        if options.get('business_unit'):
            business_units = [
                c.get('id') for c in options['business_unit'] if c.get('selected')]
            business_units = business_units if len(business_units) > 0 else [c.get('id')
                                                                             for c in options['business_unit']]
        context['business_units'] = len(business_units) > 0 and business_units
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
             SUM(balance * (EML.encryption / 100) /
                             (
                                 CASE
                                   WHEN BURL.sign
                                           THEN -1 * (CASE
                                                        WHEN AML.company_currency_id = 2
                                                                THEN 1
                                                        ELSE RCR.rate
                                     END
                                     )
                                   ELSE (
                                     CASE
                                       WHEN AML.company_currency_id = 2
                                               THEN 1
                                       ELSE RCR.rate
                                         END
                                     )
                                     END
                                 )
            )  AS balance,
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
        common_tables_tag = common_tables.format(
            'business_unit_tag BUT', 'tag', 'BUT', 'BUT', 'tag')
        common_tables_group = common_tables.format(
            'business_unit_group BUG', 'group', 'BUG', 'BUG', 'group')

        account_tables = """
            JOIN account_account AA_ID ON (AA_ID.id = BUML.account_id)
            JOIN account_account AA ON (AA.code = AA_ID.code)
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

        move_currency_tables = """
            JOIN account_move_line AML ON (AML.account_id = AA.id AND
                                            AML.company_id IN (2, 3, 4, 5, 6, 7) AND AML.date >= %s AND
                                            AML.date <= %s)
             JOIN account_move AM ON (AML.move_id = AM.id)
             LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                              AND RCR.name = date_trunc('month', AML.date) :: date)
             JOIN encryption_mapping_line EML ON (EML.analytical_account_id = AML.analytic_account_id AND
                                                  BUM.profit_center = EML.cost_center)
             JOIN encryption_mapping EM ON (EML.encryption_mapping_id = EM.id) 
             JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)  
        """

        where_args = ['%s' for profit_center in context['business_units']]
        where = """
            WHERE AA.code SIMILAR TO %s
            AND AA.code != '999999'
            AND AM.state = %s
            AND BUM.profit_center in ({})
            AND AFY.date_to >= %s AND AFY.date_from <= %s
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

        select_tag_accounts = select_fields_tag + common_tables_tag + account_tables + move_currency_tables + where + \
            group_by_tag
        select_group_accounts = select_fields_group + common_tables_group + account_tables + move_currency_tables + \
            where + group_by_group
        select_tag_account_tag = select_fields_tag + common_tables_tag + account_tag_tables + move_currency_tables + \
            where + group_by_tag
        select_group_account_tag = select_fields_group + common_tables_group + account_tag_tables + \
            move_currency_tables + where + group_by_group
        select_tag_account_group = select_fields_tag + common_tables_tag + account_group_tables + move_currency_tables \
            + where + group_by_tag
        select_group_account_group = select_fields_group + common_tables_group + account_group_tables + move_currency_tables \
            + where + group_by_group
        select_tag_expression = select_fields_tag + common_tables_tag + account_expression_tables + \
            move_currency_tables + where + where_cond_expression + group_by_tag
        select_group_expression = select_fields_group + common_tables_group + account_expression_tables + \
            move_currency_tables + where + where_cond_expression + group_by_group

        sql = select_all + select_tag_accounts + union + select_group_accounts + union + select_tag_account_tag + \
            union + select_group_account_tag + union + select_tag_account_group + union + select_group_account_group \
            + union + select_tag_expression + union + \
            select_group_expression + union + select_all_empty + end_select

        params_profit_center = tuple(
            profit_center for profit_center in context['business_units'])

        params = ('%',) + params_profit_center + \
                 ((context.get('date_from'), context.get('date_to'), '(4|8|9)%', 'posted') + params_profit_center +
                  (context.get('date_from'), context.get('date_to'))) * 8 + params_profit_center

        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _do_query_overhead(self):
        context = dict(self._context or {})

        sql = """
            WITH REPORT AS (SELECT DISTINCT BUM.profit_center AS profit_center_id, EML.encryption AS overhead
                            FROM business_unit_mapping BUM
                                   JOIN account_analytic_account AAA_BUM ON (BUM.profit_center = AAA_BUM.id)
                                   JOIN account_analytic_account AAA
                                     ON (AAA.code = ('7' || Substring(AAA_BUM.code FROM 2 FOR CHAR_LENGTH(AAA_BUM.code) - 1)))
                                   JOIN encryption_mapping_line EML ON (EML.cost_center = AAA.id)
                                   JOIN encryption_mapping EM ON (EM.id = EML.encryption_mapping_id)
                                   JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)
                            WHERE AFY.date_from <= %s
                              AND AFY.date_to >= %s),
                 OVERHEAD_BALANCE AS (SELECT COALESCE(SUM(
                                               balance * (EML.encryption / 100) /
                                               (
                                                   CASE
                                                     WHEN AML.company_currency_id = 2
                                                             THEN 1
                                                     ELSE RCR.rate
                                                       END
                                                   )
                                                 ), 0) AS balance
                                      FROM encryption_mapping EM
                                             JOIN account_fiscal_year AFY ON (AFY.id = EM.fiscal_year)
                                             JOIN encryption_mapping_line EML on (EM.id = EML.encryption_mapping_id)
                                             JOIN account_move_line AML ON (AML.analytic_account_id = EML.analytical_account_id)
                                             JOIN account_move AM ON (AM.id = AML.move_id)
                                             JOIN account_account AA ON (AML.account_id = AA.id)
                                             LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                                                   AND
                                                                                 RCR.name = date_trunc('month', AML.date) :: date)
                                      WHERE AFY.date_from <= %s
                                        AND AFY.date_to >= %s
                                        AND EML.cost_center =
                                            (SELECT id FROM account_analytic_account WHERE code LIKE %s
                                                                                       AND name LIKE %s limit 1)
                                        AND AA.code SIMILAR TO %s
                                        AND AA.code != '999999'
                                        AND AML.date <= %s
                                        AND AML.date >= %s
                                        AND AM.state = %s)
            SELECT OVERHEAD_BALANCE.balance * REPORT.overhead / 100 AS balance, profit_center_id
            FROM REPORT
                   CROSS JOIN OVERHEAD_BALANCE;
        """
        params = (context.get('date_to'), context.get('date_to'), context.get('date_to'), context.get('date_to'), '6%',
                  '%OVERHEAD%', '(4|8|9)%', context.get('date_to'), context.get('date_from'), 'posted')
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return {row['profit_center_id']: row['balance'] for row in results}

    def _resolve_formula(self, options, line_id):
        context = dict(self._context or {})
        results = self._do_query(options, line_id)
        overhead = self._do_query_overhead()
        business_units = []
        if options.get('business_unit'):
            business_units = [
                c.get('id') for c in options['business_unit'] if c.get('selected')]
            business_units = business_units if len(business_units) > 0 else [c.get('id')
                                                                             for c in options['business_unit']]
        context['business_units'] = len(business_units) > 0 and business_units
        for profit_center_id in context['business_units']:
            results_by_code = {'E{}'.format(result['id']): result['balance'] for result in results
                               if result['profit_center_id'] == profit_center_id}
            results_by_code['result'] = 0
            for i, result in enumerate(results):
                if result['profit_center_id'] == profit_center_id and result['type'] == 'overhead':
                    try:
                        results[i]['balance'] = overhead[profit_center_id]
                        results_by_code['E{}'.format(
                            result['id'])] = overhead[profit_center_id]
                    except KeyError:
                        pass
                if result['profit_center_id'] == profit_center_id and result['type'] == 'total':
                    formula = 'result = {}'.format(
                        re.sub(r"([0-9]+(\.[0-9]+)?)", r"E\1", result['formula']).strip())
                    safe_eval(formula, results_by_code,
                              mode='exec', nocopy=True)
                    results_by_code['E{}'.format(
                        result['id'])] = results_by_code['result']
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
