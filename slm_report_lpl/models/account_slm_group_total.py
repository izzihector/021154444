# -*- coding: utf-8 -*-

import re
from decimal import Decimal
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError 


class AccountSLMGroupTotalReport(models.AbstractModel):
    _name = "account.slm.group.total.report"
    _description = "SLM Group Report"
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
    filter_business_unit = None
    MAX_LINES = None
    columns = 10

    @api.model
    def _get_report_name(self):
        sql = """
            SELECT name FROM slm_group_total_mapping WHERE id = 1
        """
        self.env.cr.execute(sql)
        results = self.env.cr.fetchone()
        try:
            name = results[0]
        except IndexError:
            name = ''
        return _(name)

    def _get_templates(self):
        templates = super(AccountSLMGroupTotalReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''}] * self.columns

    def _do_query(self, options, line_id, limit=False):
        context = dict(self._context or {})

        select_all = """
            SELECT id, sequence, name, formula, type,
                   array_agg(profit_center ORDER BY profit_center_id) as profit_center,
                   array_agg(balance ORDER BY profit_center_id) as balance,
                   array_agg(profit_center_id ORDER BY profit_center_id) as profit_center_id
            FROM (
                  SELECT id, sequence, name, formula, type, profit_center, sum(balance) as balance, profit_center_id
                  FROM (
        """

        select_expression = """
                   WITH accounts_expression AS (
                        SELECT DISTINCT expression, AA.id
                                 FROM slm_group_total_mapping SGTM
                                        JOIN slm_group_mapping_slm_group_total_mapping_rel SGMSGTMR
                                          ON (SGTM.id = SGMSGTMR.slm_group_total_mapping_id)
                                        JOIN slm_group_mapping SGM ON (SGM.id = SGMSGTMR.slm_group_mapping_id)
                                        JOIN slm_group_mapping_line SGML ON (SGML.slm_group_mapping_id = SGM.id)
                                        JOIN account_account AA ON (AA.code LIKE CONCAT(SGML.expression, %s))
                                 WHERE SGM.id = 1
                                   AND SGML.expression IS NOT NULL
                  )
        """
        select_all += select_expression

        select_fields = """
            SELECT SGRL.id,
             SGRL.sequence,
             SGM.name AS profit_center,
             SGM.id   AS profit_center_id,
             {}.name,
             SUM(balance * (EML.encryption / 100) /
                 (
                     CASE
                       WHEN SGRL.sign
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
                 )    AS balance,
             SGRL.formula,
             SGRL.type
        """

        select_fields_group = select_fields.format('SGG')
        select_fields_tag = select_fields.format('SGT')

        common_tables = """
            FROM slm_group_total_mapping SGTM
             JOIN slm_group_mapping_slm_group_total_mapping_rel SGMSGTMR
               ON (SGTM.id = SGMSGTMR.slm_group_total_mapping_id)
             JOIN slm_group_mapping SGM ON (SGM.id = SGMSGTMR.slm_group_mapping_id)
             JOIN slm_group_mapping_line SGML ON (SGML.slm_group_mapping_id = SGM.id)
             JOIN slm_group_report_layout SGRL
               ON (SGRL.slm_group_total_mapping_id = SGTM.id AND SGML.{0} = SGRL.{0})
             JOIN slm_group_{0} {1} ON (SGML.{0} = {1}.id)
        """

        common_tables_group = common_tables.format('group', 'SGG')
        common_tables_tag = common_tables.format('tag', 'SGT')

        account_tables = """
            JOIN account_account AA_ID ON SGML.account_id = AA_ID.id
            JOIN account_account AA ON (AA.code = AA_ID.code)
        """

        account_tag_tables = """
            JOIN account_account_account_tag AAAT ON (AAAT.account_account_tag_id = SGML.tag_id)
            JOIN account_account AA ON (AAAT.account_account_id = AA.id)
        """

        account_group_tables = """
            JOIN account_account AA ON (AA.group_id = SGML.group_id)
        """

        account_expression_tables = """
            JOIN accounts_expression ON (accounts_expression.expression = SGML.expression)
            JOIN account_account AA ON (accounts_expression.id = AA.id)
        """

        move_currency_tables = """
            JOIN account_move_line AML ON (AA.id = AML.account_id AND
                                            AML.company_id IN (2, 3, 4, 5, 6, 7) AND AML.date >= %s AND
                                            AML.date <= %s)
            JOIN account_move AM ON (AM.id = AML.move_id)
            LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                          AND RCR.name = date_trunc('month', AML.date) :: date)
            JOIN encryption_mapping_line EML ON (EML.analytical_account_id = AML.analytic_account_id AND
                                              SGM.profit_center = EML.cost_center)
            JOIN encryption_mapping EM ON (EML.encryption_mapping_id = EM.id) 
            JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)  
        """

        where = """
             WHERE SGTM.id = 1
                AND AA.code SIMILAR TO %s
                AND AA.code != '999999'
                AND AM.state = %s
                AND AFY.date_to >= %s AND AFY.date_from <= %s
        """

        group_by = """
            GROUP BY SGRL.id,
               SGRL.sequence,
               SGM.name,
               SGM.id,
               {}.name
        """

        group_by_tag = group_by.format('SGT')
        group_by_group = group_by.format('SGG')

        select_all_empty = """
            SELECT SGRL.id, SGRL.sequence, SGM.name AS profit_center, SGM.id AS profit_center_id,
                 COALESCE(
                            SGT.name,
                            SGG.name,
                            SGRL.name
                  ) AS name,
                     0 AS balance, SGRL.formula, SGRL.type
              FROM slm_group_report_layout SGTM
                     JOIN slm_group_mapping_slm_group_total_mapping_rel SGMSGTMR
                       ON (SGMSGTMR.slm_group_total_mapping_id = SGTM.id)
                     JOIN slm_group_mapping SGM ON (SGM.id = SGMSGTMR.slm_group_mapping_id)
                     JOIN slm_group_report_layout SGRL ON (SGTM.id = SGRL.slm_group_total_mapping_id)
                     LEFT JOIN slm_group_tag SGT ON (SGRL.tag = SGT.id)
                     LEFT JOIN slm_group_group SGG ON (SGRL.group = SGG.id)
              WHERE SGTM.id = 1
                AND (
                        SGT.name IS NOT NULL
                          OR SGG.name IS NOT NULL
                          OR SGRL.name IS NOT NULL
                        )
              GROUP BY COALESCE(
                         SGT.name,
                         SGG.name,
                         SGRL.name
                  ),
                       SGM.name,
                       SGM.id,
                       SGRL.sequence,
                       SGRL.formula,
                       balance,
                       SGRL.type,
                       SGRL.id
        """

        end_select = """
                ) AS A
                  GROUP BY id,
                           sequence,
                           name,
                           formula,
                           type,
                           profit_center,
                           profit_center_id
             ) AS B
            GROUP BY id,
                     sequence,
                     name,
                     formula,
                     type
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
        select_group_account_group = select_fields_group + common_tables_group + account_group_tables + \
                                     move_currency_tables + where + group_by_group
        select_tag_expression = select_fields_tag + common_tables_tag + account_expression_tables + \
                                move_currency_tables + where + group_by_tag
        select_group_expression = select_fields_group + common_tables_group + account_expression_tables + \
                                  move_currency_tables + where + group_by_group

        sql = select_all + select_tag_accounts + union + select_group_accounts + union + select_tag_account_tag + \
              union + select_group_account_tag + union + select_tag_account_group + union + select_group_account_group \
              + union + select_tag_expression + union + select_group_expression + union + select_all_empty + end_select

        params = ('%',) + (context.get('date_from'), context.get('date_to'), '(4|8|9)%', 'posted',
                           context.get('date_from'), context.get('date_to')) * 8
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _do_query_overhead(self):
        context = dict(self._context or {})

        sql = """
            WITH REPORT AS (SELECT DISTINCT SGM.id, EML.encryption AS overhead
                            FROM slm_group_mapping SGM
                                   JOIN account_analytic_account AAA_SGM ON (SGM.profit_center = AAA_SGM.id)
                                   JOIN account_analytic_account AAA
                                     ON (AAA.code = ('7' || Substring(AAA_SGM.code FROM 2 FOR CHAR_LENGTH(AAA_SGM.code) - 1)))
                                   JOIN encryption_mapping_line EML ON (EML.cost_center = AAA.id)
                                   JOIN encryption_mapping EM ON (EM.id = EML.encryption_mapping_id)
                                   JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)
                            WHERE AFY.date_from <= %s
                              AND AFY.date_to >= %s),
                 OVERHEAD_BALANCE AS (SELECT SUM(
                                               balance * (EML.encryption / 100) /
                                               (
                                                   CASE
                                                     WHEN AML.company_currency_id = 2
                                                             THEN 1
                                                     ELSE RCR.rate
                                                       END
                                                   )
                                                 ) AS balance
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
            SELECT COALESCE(OVERHEAD_BALANCE.balance * REPORT.overhead / 100, 0) AS balance, id
            FROM REPORT
                   CROSS JOIN OVERHEAD_BALANCE;
        """
        params = (context.get('date_to'), context.get('date_to'), context.get('date_to'), context.get('date_to'), '6%',
                  '%OVERHEAD%', '(4|8|9)%', context.get('date_to'), context.get('date_from'), 'posted')
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return {row['id']: row['balance'] for row in results}

    def _get_profit_centers(self, field='id'):
        sql = """
            SELECT {} FROM slm_group_mapping ORDER BY id
        """.format(field)
        self.env.cr.execute(sql)
        results = self.env.cr.fetchall()
        return [row[0] for row in results]

    def _resolve_formula(self, options, line_id):
        results = self._do_query(options, line_id)
        profit_centers = self._get_profit_centers()
        overhead = self._do_query_overhead()
        for index, profit_center_id in enumerate(profit_centers):
            results_by_code = {'E{}'.format(result['id']): result['balance'][index] for result in results}
            results_by_code['result'] = 0
            for i, result in enumerate(results):
                if result['name'] == 'OVERHEAD':
                    try:
                        results[i]['balance'][index] = float(overhead[profit_center_id])
                        results_by_code['E{}'.format(result['id'])] = Decimal(overhead[profit_center_id])
                    except KeyError:
                        pass
                if result['type'] == 'total':
                    formula = 'result = {}'.format(re.sub(r"([0-9]+(\.[0-9]+)?)", r"E\1", result['formula']).strip())
                    safe_eval(formula, results_by_code, mode='exec', nocopy=True)
                    results_by_code['E{}'.format(result['id'])] = results_by_code['result']
                    results[i]['balance'][index] = results_by_code['result']
        return results

    def _get_lines(self, options, line_id=None):
        rows = self._resolve_formula(options, line_id)
        lines = []
        name = self._get_report_name()
        profit_centers = self._get_profit_centers('name')

        lines.append({
            'id': 'header',
            'name': name,
            'title_hover': name,
            'columns': [],
            'level': 1,
            'unfoldable': False,
            'colspan': 8,
            'style': 'text-align:center;font-size:15px;background-color:lightblue'
        })
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
        lines.append({
            'id': 'profit_centers',
            'name': '',
            'title_hover': 'profit_centers',
            'columns': [{'name': v} for v in profit_centers] + [{'name': 'TOTAAL'}],
            'level': 2,
            'unfoldable': False,
            'colspan': 1,
            'style': 'text-align:right;font-size:14px;background-color:#eff5f7'
        })

        for row in rows:
            if row['type'] == 'tag':
                lines.append({
                    'id': row['name'],
                    'name': row['name'],
                    'title_hover': row['name'],
                    'columns': [{'name': round(v, 2), 'style': 'text-align:right'} for v in row['balance']] +
                               [{'name': round(sum(row['balance']), 2), 'style': 'text-align:right'}],
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
                    'columns': [{'name': round(v, 2), 'style': 'text-align:right'} for v in row['balance']] +
                               [{'name': round(sum(row['balance']), 2), 'style': 'text-align:right'}],
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
                    'columns': [{'name': round(v, 2), 'style': 'text-align:right'} for v in row['balance']] +
                               [{'name': round(sum(row['balance']), 2), 'style': 'text-align:right'}],
                    'level': 3,
                    'unfoldable': False,
                    'colspan': 1,
                    'style': 'text-align:left;width:10%'
                })
        return lines
