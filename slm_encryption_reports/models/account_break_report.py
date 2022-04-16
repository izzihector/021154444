# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from dateutil.parser import parse


class AccountBreakReport(models.AbstractModel):
    _name = "account.break.report"
    _description = "Break Report"
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
        return _("Result overview per route")

    def _get_templates(self):
        templates = super(AccountBreakReport, self)._get_templates()
        templates['line_template'] = 'slm_encryption_reports.line_template'
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''}] * self.columns

    def _set_context(self, options):
        ctx = super(AccountBreakReport, self)._set_context(options)
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
        options = super(AccountBreakReport, self)._get_options(previous_options)
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
                                balance * (EML.encryption / 100) /
                                (
                                    CASE
                                        WHEN AML.company_currency_id = 2
                                            THEN 1
                                        ELSE RCR.rate
                                        END
                                )
                        )) * (CASE WHEN PCMLPV.value > 0 THEN PCMLPV.value/100 ELSE 1 END)
                    ELSE SUM(
                                balance * (EML.encryption / 100) /
                                (
                                    CASE
                                        WHEN AML.company_currency_id = 2
                                            THEN 1
                                        ELSE RCR.rate
                                        END
                                    )
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
                  JOIN account_move_line AML ON (AML.account_id = AA_CODE.id AND
                                             AML.company_id IN (2, 3, 4, 5, 6, 7) AND AML.date >= %s AND
                                             AML.date <= %s)
        """

        join_analytical_accounts = """
                  JOIN account_analytic_account AAA ON (AAA.id = PCML.analytical_account_id)
                  JOIN account_move_line AML ON (AML.analytic_account_id = AAA.id AND
                                             AML.company_id IN (2, 3, 4, 5, 6, 7) AND AML.date >= %s AND
                                             AML.date <= %s)
                  JOIN account_account AA_CODE ON (AML.account_id = AA_CODE.id)  
        """

        join_currency_encryption = """
                  JOIN account_move AM ON (AML.move_id = AM.id)
                  LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                     AND RCR.name = date_trunc('month', AML.date)::date)
                  JOIN encryption_mapping_line EML
                            ON (EML.analytical_account_id = AML.analytic_account_id AND
                                PCR.profit_center = EML.cost_center)    
        """

        where_args = ['%s' for profit_center_id in context['profit_centers']]
        where = """
            WHERE PCM.id = 1
                AND (AA_CODE.code SIMILAR TO %s  OR AA_CODE ISNULL)
                AND (AA_CODE.code != '999999' OR AA_CODE ISNULL )
                AND (AM.state = 'posted' OR AM.state ISNULL)
                AND PCR.id in ({})
                AND AA_CODE.id NOT IN (SELECT account_account_id FROM account_account_account_tag 
                    WHERE account_account_tag_id = PCML.excluded_account_tag)
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
                              join_currency_encryption + where + group_by_group

        sql_groups_analytical_accounts = select_fields_group + common_tables_group + join_analytical_accounts + \
                                         join_currency_encryption + where + group_by_group

        sql_tags_accounts = select_fields_tag + common_tables_tag + join_accounts + \
                            join_currency_encryption + where + group_by_tag

        sql_tags_analytical_accounts = select_fields_tag + common_tables_tag + join_analytical_accounts + \
                                       join_currency_encryption + where + group_by_tag

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
        params = ((context.get('date_from'), context.get('date_to'), '(4|8|9)%') + params_profit_center) * 4 + \
                 params_profit_center
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _do_query_overhead(self, profit_center_id):
        sql = """
             WITH REPORT AS (
                SELECT * FROM profit_center_report PCR WHERE PCR.profit_center_mapping_id = 1 AND PCR.id = %s),
             OVERHEAD_BALANCE AS (
                 SELECT %s AS report_id,
                        SUM(
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
                     AND RCR.name = date_trunc('month', AML.date)::date)
                 WHERE AFY.date_from <= %s
                   AND AFY.date_to >= %s
                   AND EML.cost_center =
                       (SELECT id FROM account_analytic_account 
                        WHERE code LIKE %s AND name LIKE %s limit 1)
                   AND AA.code SIMILAR TO %s
                   AND AA.code != '999999'
                   AND AML.date <= %s
                   AND AML.date >= %s
                   AND AM.state = 'posted'
             )
            SELECT REPORT.overhead, COALESCE(OVERHEAD_BALANCE.balance * REPORT.overhead / 100, 0) AS balance
            FROM REPORT
                     JOIN OVERHEAD_BALANCE ON (REPORT.id = OVERHEAD_BALANCE.report_id)
        """
        context = dict(self._context or {})
        params = profit_center_id, profit_center_id, context.get('date_to'), context.get('date_to'), '6%', \
                 '%OVERHEAD%', '(4|8|9)%', context.get('date_to'), context.get('date_from')
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _do_query_vlnr(self, options, profit_centers):

        select_all = """
            SELECT sequence, name, type, formula, id, array_agg(profit_center) AS profit_center,
                array_agg(balance) AS balance, array_agg(flight_number) as flight_number, 
                array_agg(route) as route
            FROM (
                SELECT sequence, name, type, formula, id, profit_center,
                    sum(balance) as balance, route,
                       string_agg(flight_number, ' - ') as flight_number
                FROM (
                         SELECT sequence,
                                profit_center,
                                name,
                                sum(balance) as balance,
                                type,
                                formula,
                                id,
                                flight_number,
                                route
                         FROM (
        """

        select_fields = """
            SELECT PCR.id AS profit_center,
                             PCRBL.sequence,
                             PCRBL.type,
                             PCRBL.formula,
                             {}.name,
                             CONCAT(FL.name, '/', FL_RE.name) AS flight_number,
                             CONCAT(FLS1.name, ' - ', FLS2.name,
                                    CASE
                                        WHEN FL.stop3 IS NOT NULL
                                            THEN CONCAT(' - ', FLS3.name)
                                        ELSE ''
                                        END,
                                    CASE
                                        WHEN FL.stop4 IS NOT NULL
                                            THEN CONCAT(' - ', FLS4.name)
                                        ELSE ''
                                        END
                                 )                            AS route,
                             {}
                             PCRBL.id
        """
        field_balance = """
            COALESCE(
                 CASE
                     WHEN PCRBL.sign
                         THEN -1 * (SUM(
                                 balance * (EML.encryption / 100) /
                                 (
                                     CASE
                                         WHEN AML.company_currency_id = 2
                                             THEN 1
                                         ELSE RCR.rate
                                         END
                                     )
                         )) * (CASE WHEN PCMLPV.value > 0 THEN PCMLPV.value / 100 ELSE 1 END)
                     ELSE SUM(
                                      balance * (EML.encryption / 100) /
                                      (
                                          CASE
                                              WHEN AML.company_currency_id = 2
                                                  THEN 1
                                              ELSE RCR.rate
                                              END
                                          )
                              ) * (CASE WHEN PCMLPV.value > 0 THEN PCMLPV.value / 100 ELSE 1 END)
                     END,
                 0
             )                            AS balance,
        """
        field_zero_balance = """
            0 AS balance,
        """

        select_fields_group = select_fields.format('PCG', field_balance)
        select_fields_tag = select_fields.format('PCT', field_balance)
        select_fields_title_total = select_fields.format('PCRBL', field_zero_balance)
        select_fields_tag_zero_balance = select_fields.format('PCT', field_zero_balance)
        select_fields_group_zero_balance = select_fields.format('PCG', field_zero_balance)

        common_tables = """
            FROM profit_center_mapping PCM
                JOIN profit_center_mapping_line PCML ON (PCM.id = PCML.profit_center_mapping_id)                            
        """

        title_total_tables = """
            FROM profit_center_mapping PCM
                JOIN profit_center_report_break_layout PCRBL ON (PCM.id = PCRBL.profit_center_mapping_id)
                JOIN profit_center_report PCR ON (PCR.profit_center_mapping_id = PCM.id AND PCR.id =2)
        """

        join_group_tables = """
           JOIN profit_center_group PCG ON (PCML.group = PCG.id)
           JOIN profit_center_report_break_layout PCRBL ON (PCRBL.group = PCML.group)
           JOIN profit_center_report PCR ON (PCR.profit_center_mapping_id = PCM.id AND PCR.id = 2)
        """

        join_tag_tables = """
            JOIN profit_center_tag PCT ON (PCML.tag = PCT.id)
            JOIN profit_center_report_break_layout PCRBL ON (PCRBL.tag = PCML.tag)
            JOIN profit_center_report PCR ON (PCR.profit_center_mapping_id = PCM.id AND PCR.id = 2)
        """

        join_partial_value = """
             LEFT JOIN profit_center_mapping_line_partial_value PCMLPV ON
              (PCMLPV.profit_center_mapping_line_id = PCML.id AND PCMLPV.report = PCR.id)
        """

        join_cross_flight = """
            CROSS JOIN flight_list FL
            JOIN flight_list FL_RE ON (FL.retvlnr = FL_RE.id)
        """

        join_account_tables = """
            JOIN account_account AA ON (AA.id = PCML.account_id)
            JOIN account_account AA_CODE ON (AA.code = AA_CODE.code)
            JOIN account_move_line AML ON (AML.account_id = AA_CODE.id AND
                                          AML.company_id IN (2, 3, 4, 5, 6, 7) AND
                                          AML.date >= %s AND
                                          AML.date <= %s)

            JOIN account_move AM ON (AML.move_id = AM.id)
        """

        join_analytic_tables = """
            JOIN account_analytic_account AAA ON (AAA.id = PCML.analytical_account_id)
            JOIN account_move_line AML ON (AML.analytic_account_id = AAA.id AND
                                      AML.company_id IN (2, 3, 4, 5, 6, 7) AND
                                      AML.date >= %s AND
                                      AML.date <= %s)
            JOIN account_account AA_CODE ON (AML.account_id = AA_CODE.id)
            JOIN account_move AM ON (AML.move_id = AM.id)
        """

        join_currency_encryption = """
            LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                      AND RCR.name = date_trunc('month', AML.date)::date)
           JOIN encryption_mapping_line EML
                ON (EML.analytical_account_id = AML.analytic_account_id AND
                    PCR.profit_center = EML.cost_center)
        """

        join_return_flight = """
            JOIN flight_list FL_RE ON (AML.vlnr = FL_RE.id)
            JOIN flight_list FL ON (FL.retvlnr = FL_RE.id)
        """

        join_flight = """
            JOIN flight_list FL ON (AML.vlnr = FL.id)
            JOIN flight_list FL_RE ON (Fl.retvlnr = FL_RE.id)      
        """

        join_stops = """
            JOIN flight_list_stop FLS1 ON (FLS1.id = FL.stop1)
            JOIN flight_list_stop FLS2 ON (FLS2.id = FL.stop2)
            LEFT JOIN flight_list_stop FLS3 ON (FLS3.id = FL.stop3)
            LEFT JOIN flight_list_stop FLS4 ON (FLS4.id = FL.stop4)
        """

        where_args = ['%s' for profit_center_id in profit_centers]
        where = """
            WHERE PCM.id = 1
                AND AA_CODE.code SIMILAR TO %s
                AND AA_CODE.code != '999999'
                AND AM.state = %s
                    OR AM.state ISNULL
                AND PCR.id in ({})
        """.format(','.join(where_args))

        where_empty_fields = """
            WHERE PCM.id = 1
                AND PCR.id in ({})
                AND FL.retvlnr IS NOT NULL
                AND FL.opercde1 = PCR.id
        """.format(','.join(where_args))

        where_total_title = """
            WHERE PCM.id = 1
                AND PCRBL.type IN ('tittle', 'total', 'overhead')
                AND FL.opercde1 = PCR.id
        """

        group_by = """
             GROUP BY PCRBL.sequence,
               {}.name,
               PCRBL.sign,
               PCRBL.type,
               PCRBL.formula,
               PCRBL.id,
               PCR.id,
               PCMLPV.value,
               FL.name, FL_RE.name,
               FLS1.name, FLS2.name, FLS3.name, FLS4.name,
               FL.stop1, FL.stop2, FL.stop3, FL.stop4
        """

        group_by_group = group_by.format('PCG')
        group_by_tag = group_by.format('PCT')

        group_by_empty_fields = """
            GROUP BY PCRBL.sequence,
               {}.name,
               PCRBL.sign,
               PCRBL.type,
               PCRBL.formula,
               PCRBL.id,
               PCR.id,
               FL.name, FL_RE.name,
               FLS1.name, FLS2.name, FLS3.name, FLS4.name,
               FL.stop1, FL.stop2, FL.stop3, FL.stop4
        """

        group_by_empty_fields_group = group_by_empty_fields.format('PCG')
        group_by_empty_fields_tag = group_by_empty_fields.format('PCT')
        group_by_title_total = group_by_empty_fields.format('PCRBL')

        union = """
            UNION ALL
        """

        end_select = """
                            ) AS A
                        GROUP BY profit_center, sequence, name, type, formula, id, flight_number, route
                        ORDER BY sequence, profit_center, flight_number
                    ) AS B
                GROUP BY sequence, name, type, formula, id, profit_center, route
                ) AS C
            GROUP BY sequence, name, type, formula, id;
        """

        select_group_account_return_flight = select_fields_group + common_tables + join_group_tables + \
                                             join_partial_value + join_account_tables + join_currency_encryption + join_return_flight + join_stops + \
                                             where + group_by_group

        select_group_account_flight = select_fields_group + common_tables + join_group_tables + \
                                      join_partial_value + join_account_tables + join_currency_encryption + join_flight + join_stops + \
                                      where + group_by_group

        select_group_analytic_return_flight = select_fields_group + common_tables + join_group_tables + \
                                              join_partial_value + join_analytic_tables + join_currency_encryption + join_return_flight + join_stops + \
                                              where + group_by_group

        select_group_analytic_flight = select_fields_group + common_tables + join_group_tables + \
                                       join_partial_value + join_analytic_tables + join_currency_encryption + join_flight + join_stops + \
                                       where + group_by_group

        select_tag_account_return_flight = select_fields_tag + common_tables + join_tag_tables + \
                                           join_partial_value + join_account_tables + join_currency_encryption + join_return_flight + join_stops + \
                                           where + group_by_tag

        select_tag_account_flight = select_fields_tag + common_tables + join_tag_tables + \
                                    join_partial_value + join_account_tables + join_currency_encryption + join_flight + join_stops + \
                                    where + group_by_tag

        select_tag_analytic_return_flight = select_fields_tag + common_tables + join_tag_tables + \
                                            join_partial_value + join_analytic_tables + join_currency_encryption + join_return_flight + join_stops + \
                                            where + group_by_tag

        select_tag_analytic_flight = select_fields_tag + common_tables + join_tag_tables + \
                                     join_partial_value + join_analytic_tables + join_currency_encryption + join_flight + join_stops + \
                                     where + group_by_tag

        select_tag_empty_fields_flight_return = select_fields_tag_zero_balance + common_tables + join_tag_tables + \
                                                join_cross_flight  + join_stops + \
                                                where_empty_fields + group_by_empty_fields_tag

        select_group_empty_fields_flight_return = select_fields_group_zero_balance + common_tables + join_group_tables + \
                                                  join_cross_flight + join_stops + \
                                                  where_empty_fields + group_by_empty_fields_group

        select_title_total_ = select_fields_title_total + title_total_tables + join_cross_flight + \
                              join_stops + where_total_title + group_by_title_total

        params_profit_center = tuple(profit_center_id for profit_center_id in profit_centers)
        context = dict(self._context or {})
        params = ((context.get('date_from'), context.get('date_to'), '(4|8|9)%', 'posted') + params_profit_center) \
                 * 9 + params_profit_center * 3

        sql = select_all + select_group_account_return_flight + union + select_group_account_flight + union +\
              select_group_analytic_return_flight + union + select_group_analytic_flight + union + \
              select_tag_account_return_flight + union + select_tag_account_flight + union + \
              select_tag_analytic_return_flight + union + select_tag_analytic_flight + union + \
              select_tag_analytic_flight + union + select_tag_empty_fields_flight_return + union + \
              select_tag_empty_fields_flight_return + union + select_group_empty_fields_flight_return + \
              union + select_title_total_ + end_select
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def _do_query_flight_data(self, options):
        context = dict(self._context or {})
        profit_centers = context['profit_centers']
        where_args = ['%s' for profit_center_id in profit_centers]

        sql = """
            SELECT profit_center, SUM(total_seats) as SS, SUM(total_pax) as PS,
                SUM(total_blockhours) AS BHS, SUM(total_kilograms) AS KGS, SUM(total_flights) AS SFS,
                route
            FROM (
                 SELECT FL.opercde1                      AS profit_center,
                        CONCAT(FLS1.name, ' - ', FLS2.name,
                               CASE
                                   WHEN FL.stop3 IS NOT NULL
                                       THEN CONCAT(' - ', FLS3.name)
                                   ELSE ''
                                   END,
                               CASE
                                   WHEN FL.stop4 IS NOT NULL
                                       THEN CONCAT(' - ', FLS4.name)
                                   ELSE ''
                                   END
                            )                            AS route,
                        AD.total_seats,
                        AD.total_pax,
                        AD.total_blockhours,
                        AD.total_kilograms,
                        AD.total_flights
                 FROM flight_list FL
                          JOIN flight_list FL_RE ON (FL.retvlnr = FL_RE.id)
                          JOIN flight_list_stop FLS1 ON (FLS1.id = FL.stop1)
                          JOIN flight_list_stop FLS2 ON (FLS2.id = FL.stop2)
                          LEFT JOIN flight_list_stop FLS3 ON (FLS3.id = FL.stop3)
                          LEFT JOIN flight_list_stop FLS4 ON (FLS4.id = FL.stop4)
                          JOIN airfare_details AD on (FL.id = AD.vlnr)
                 WHERE AD.date >= %s
                    AND AD.date <= %s
                    AND FL.opercde1 in ({})
                 ORDER BY FL.opercde1, FL.name
             ) AS A
            GROUP BY profit_center, route
            ORDER BY profit_center, route
        """.format(','.join(where_args))

        params_profit_center = tuple(profit_center_id for profit_center_id in profit_centers)
        params = (context.get('date_from'), context.get('date_to')) + params_profit_center
        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        return results

    def grouped_flight_data(self, options):
        results = self._do_query_flight_data(options)
        grouped_data = {}
        for result in results:
            profit_center = result['profit_center']
            route = result['route']
            if profit_center not in grouped_data:
                grouped_data[profit_center] = {}
            grouped_data[profit_center][route] = {}
            grouped_data[profit_center][route]['SS'] = result['ss']
            grouped_data[profit_center][route]['PS'] = result['ps']
            grouped_data[profit_center][route]['BHS'] = result['bhs']
            grouped_data[profit_center][route]['KGS'] = result['kgs']
            grouped_data[profit_center][route]['SFS'] = result['sfs']

        for profit_center in grouped_data:
            spc = ppc = bhpc = kgpc = sfpc = 0
            for route in grouped_data[profit_center]:
                spc += grouped_data[profit_center][route]['SS']
                ppc += grouped_data[profit_center][route]['PS']
                bhpc += grouped_data[profit_center][route]['BHS']
                kgpc += grouped_data[profit_center][route]['KGS']
                sfpc += grouped_data[profit_center][route]['SFS']
            grouped_data[profit_center]['SPC'] = spc
            grouped_data[profit_center]['PPC'] = ppc
            grouped_data[profit_center]['BHPC'] = bhpc
            grouped_data[profit_center]['KGPC'] = kgpc
            grouped_data[profit_center]['SFPC'] = sfpc

        return grouped_data

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

    def _get_profit_centers_break(self):
        context = dict(self._context or {})
        where_args = ['%s' for profit_center_id in context['profit_centers']]
        sql = """
            SELECT id FROM profit_center_report WHERE break_report AND profit_center_mapping_id = 1 
        """.format(','.join(where_args))
        params = tuple(profit_center_id for profit_center_id in context['profit_centers'])

        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()

        return [result['id'] for result in results]

    def _get_routes(self):
        sql = """
            SELECT profit_center, string_agg(flight_number, ' - ') as flight_number, route
            FROM (
                     SELECT FL.opercde1                      AS profit_center,
                            CONCAT(FL.name, '/', FL_RE.name) AS flight_number,
                            CONCAT(FLS1.name, ' - ', FLS2.name,
                                   CASE
                                       WHEN FL.stop3 IS NOT NULL
                                           THEN CONCAT(' - ', FLS3.name)
                                       ELSE ''
                                       END,
                                   CASE
                                       WHEN FL.stop4 IS NOT NULL
                                           THEN CONCAT(' - ', FLS4.name)
                                       ELSE ''
                                       END
                                )                            AS route
                     FROM flight_list FL
                              JOIN flight_list FL_RE ON (FL.retvlnr = FL_RE.id)
                              JOIN flight_list_stop FLS1 ON (FLS1.id = FL.stop1)
                              JOIN flight_list_stop FLS2 ON (FLS2.id = FL.stop2)
                              LEFT JOIN flight_list_stop FLS3 ON (FLS3.id = FL.stop3)
                              LEFT JOIN flight_list_stop FLS4 ON (FLS4.id = FL.stop4)
                     ORDER BY FL.opercde1, FL.name
                 ) AS A
            GROUP BY profit_center, route
            ORDER BY profit_center, route;
        """
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        grouped = {}
        for result in results:
            profit_center = result['profit_center']
            if profit_center not in grouped:
                grouped[profit_center] = collections.OrderedDict()
            grouped[profit_center][result['route']] = result['flight_number']
        return grouped

    def _get_grouped_analytic_accounts(self, analytic_accounts):
        context = dict(self._context or {})
        where_args_pc = ['%s' for profit_center_id in context['profit_centers']]
        where_args_aa = ['%s' for analytic_account in analytic_accounts]
        sql = """
            SELECT PC.id as profit_center,
                   SUM(balance * (EML.encryption / 100) /
                   (
                       CASE
                           WHEN AML.company_currency_id = 2
                               THEN 1
                           ELSE RCR.rate
                           END
                       )) AS balance
            FROM account_move_line AML
                     JOIN account_move AM ON (AM.id = AML.move_id)
                     JOIN account_analytic_account AAA ON (AML.analytic_account_id = AAA.id)
                     JOIN account_account AA ON (AML.account_id = AA.id)
                     LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                        AND RCR.name = date_trunc('month', AML.date)::date)
                     JOIN encryption_mapping_line EML ON (EML.analytical_account_id = AML.analytic_account_id)
                    JOIN profit_center PC ON (PC.analytical_account_id = EML.cost_center)
            WHERE AAA.code in ({})
                AND PC.id in ({})
                AND AA.code SIMILAR TO %s
                AND AA.code != '999999'
                AND AM.state = 'posted'
                AND AML.date >= %s
                AND AML.date <= %s
            GROUP BY PC.id
            ORDER BY PC.id
        """.format(','.join(where_args_aa), ','.join(where_args_pc))

        params = (tuple(str(analytic_account) for analytic_account in analytic_accounts) +
                 tuple(profit_center_id for profit_center_id in context['profit_centers']))
        params = params + ('(4|8|9)%', context.get('date_from'), context.get('date_to'))

        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        grouped_pc = {}
        for result in results:
            profit_center = result['profit_center']
            if profit_center not in grouped_pc:
                grouped_pc[profit_center] = result['balance']

        return results

    def _get_grouped_accounts(self, accounts):
        context = dict(self._context or {})
        where_args_pc = ['%s' for profit_center_id in context['profit_centers']]
        where_args_aa = ['%s' for analytic_account in accounts]

        sql = """
        SELECT PC.id as profit_center,
               SUM(balance * (EML.encryption / 100) /
               (
                   CASE
                       WHEN AML.company_currency_id = 2
                           THEN 1
                       ELSE RCR.rate
                       END
                   )) AS balance
        FROM account_move_line AML
                 JOIN account_move AM ON (AM.id = AML.move_id)
                 JOIN account_account AA ON (AML.account_id = AA.id)
                 LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                    AND RCR.name = date_trunc('month', AML.date)::date)
                 JOIN encryption_mapping_line EML ON (EML.analytical_account_id = AML.analytic_account_id)
                JOIN profit_center PC ON (PC.analytical_account_id = EML.cost_center)
        WHERE AA.code in ({})
            AND AM.state = 'posted'
            AND PC.id in ({})
            AND AML.date >= %s
            AND AML.date <= %s
        GROUP BY PC.id
        ORDER BY PC.id
        """.format(','.join(where_args_aa), ','.join(where_args_pc))

        params = (tuple(str(account) for account in accounts) +
                  tuple(profit_center_id for profit_center_id in context['profit_centers']))
        params = params + (context.get('date_from'), context.get('date_to'))

        self.env.cr.execute(sql, params)
        results = self.env.cr.dictfetchall()
        grouped_pc = {}
        for result in results:
            profit_center = result['profit_center']
            if profit_center not in grouped_pc:
                grouped_pc[profit_center] = result['balance']
        return results

    def _group_all_data(self):
        all_data = {}
        routes = self._get_routes()
        AAA1 = self._get_grouped_analytic_accounts([53300])
        AAA2 = self._get_grouped_analytic_accounts([53000, 53001, 53002, 53301, 53302, 53303, 53304])
        AAA3 = self._get_grouped_analytic_accounts([53305])
        AA1 = self._get_grouped_accounts(([450006, 470009]))
        context = dict(self._context or {})
        for profit_center in context['profit_centers']:
            if profit_center not in all_data:
                all_data[profit_center] = {}
            try:
                all_data[profit_center]['AAA1'] = AAA1[profit_center]
            except:
                all_data[profit_center]['AAA1'] = 0

            try:
                all_data[profit_center]['AAA2'] = AAA2[profit_center]
            except:
                all_data[profit_center]['AAA2'] = 0

            try:
                all_data[profit_center]['AAA3'] = AAA3[profit_center]
            except:
                all_data[profit_center]['AAA3'] = 0

            try:
                all_data[profit_center]['AA1'] = AA1[profit_center]
            except:
                all_data[profit_center]['AA1'] = 0
        return all_data

    def _resolve_formula_stretch(self, options, report_data, flight_data):
        context = dict(self._context or {})
        profit_centers_break = self._get_profit_centers_break()
        all_variables = self._group_all_data()
        results_vlr = self._do_query_vlnr(options, profit_centers_break)
        routes = self._get_routes()
        results = []
        for ipc, profit_center in enumerate(context['profit_centers']):
            results_by_code_pc = {'E{}'.format(result['id']): result['balance'][ipc] for result in report_data}
            if profit_center not in profit_centers_break:
                for idx, result in enumerate(report_data):
                    try:
                        results[idx]['profit_center'].append(profit_center)
                        results[idx]['balance'].append(result['balance'][ipc])
                    except IndexError:
                        results.append({'sequence': result['sequence'], 'name': result['name'], 'type': result['type'],
                                        'id': result['id'], 'profit_center': [profit_center],
                                        'balance': [result['balance'][ipc]]})
                    try:
                        variables = flight_data[profit_center]
                        results[idx]['profit_center'].append(profit_center)
                        results[idx]['profit_center'].append(profit_center)
                        results[idx]['profit_center'].append(profit_center)
                        results[idx]['balance'].append(result['balance'][ipc]/variables['SFPC'])
                        results[idx]['balance'].append(result['balance'][ipc]*2/variables['SFPC'])
                        results[idx]['balance'].append(result['balance'][ipc]/variables['BHPC'])
                    except KeyError:
                        pass
            else:
                results_by_code_regio = results_by_code_pc

        for ipc, profit_center in enumerate(context['profit_centers']):
            if profit_center in profit_centers_break:
                for idx, result in enumerate(report_data):
                        results[idx]['profit_center'].append(profit_center)
                        results[idx]['balance'].append(result['balance'][ipc])

                for ir, route in enumerate(routes[2].keys()):
                    results_by_code = {'B{}'.format(result['id']): result['balance'][ir] for result in results_vlr}
                    results_by_code['result'] = 0
                    try:
                        results_by_code['PPC'] = flight_data[2]['PPC']
                        results_by_code['KGPC'] = flight_data[2]['KGPC']
                        results_by_code['SFPC'] = flight_data[2]['SFPC']
                        results_by_code['BPC'] = flight_data[2]['BHPC']
                    except KeyError:
                        results_by_code['PPC'] = 0
                        results_by_code['KGPC'] = 0
                        results_by_code['SFPC'] = 0
                        results_by_code['BPC'] = 0
                    try:
                        results_by_code['PS'] = flight_data[2][route]['PS']
                    except KeyError:
                        results_by_code['PS'] = 0
                    try:
                        results_by_code['KGS'] = flight_data[2][route]['KGS']
                    except KeyError:
                        results_by_code['KGS'] = 0
                    try:
                        results_by_code['SFS'] = flight_data[2][route]['SFS']
                    except KeyError:
                        results_by_code['SFS'] = 0
                    try:
                        results_by_code['BHS'] = flight_data[2][route]['BHS']
                    except KeyError:
                        results_by_code['BHS'] = 0
                    results_by_code['AAA1'] = all_variables[2]['AAA1']
                    results_by_code['AAA2'] = all_variables[2]['AAA2']
                    results_by_code['AAA3'] = all_variables[2]['AAA3']
                    results_by_code['AA1'] = all_variables[2]['AA1']
                    results_by_code.update(results_by_code_regio)

                    for i, result in enumerate(results_vlr):
                        # formula = 'result = {}'.format(result['formula']).strip()
                        try:
                            # safe_eval(formula, results_by_code, mode='exec', nocopy=True)
                            results_by_code['B{}'.format(result['id'])] = results_by_code['result']
                            results_vlr[i]['balance'][ir] = results_by_code['result']
                        except ValueError:
                            results_by_code['B{}'.format(result['id'])] = 0
                            results_vlr[i]['balance'][ir] = 0

                    for idx, result in enumerate(results_vlr):
                        try:
                            results[idx]['profit_center'].append(2)
                            results[idx]['balance'].append(result['balance'][ir])
                        except IndexError:
                            results.append({'sequence': result['sequence'], 'name': result['name'], 'type': result['type'],
                                            'id': result['id'], 'profit_center': [2],
                                            'balance': [result['balance'][ir]]})
                        try:
                            variables = flight_data[2]
                        except KeyError:
                            variables = {}
                        results[idx]['profit_center'].append(2)
                        results[idx]['profit_center'].append(2)
                        results[idx]['profit_center'].append(2)
                        try:
                            results[idx]['balance'].append(result['balance'][ir]/variables['SFPC'])
                        except (TypeError, KeyError):
                            results[idx]['balance'].append(0)
                        try:
                            results[idx]['balance'].append(result['balance'][ir]*2/variables['SFPC'])
                        except (TypeError, KeyError):
                            results[idx]['balance'].append(0)
                        try:
                            results[idx]['balance'].append(result['balance'][ir]/variables['BHPC'])
                        except (TypeError, KeyError):
                            results[idx]['balance'].append(0)
        return results

    def _get_stretch_data(self, options, report_data):
        flight_data = self.grouped_flight_data(options)
        return self._resolve_formula_stretch(options, report_data, flight_data)

    def _get_overhead(self, profit_center_id):
        results = self._do_query_overhead(profit_center_id)
        return results[0]

    def _get_lines(self, options, line_id=None):
        lines = []
        grouped_accounts = self._resolve_formula(options, line_id)
        routes = self._get_routes()
        context = dict(self._context or {})
        grouped_accounts = self._get_stretch_data(options, grouped_accounts)
        profit_centers = self.env['profit.center'].browse([1, 3, 2])
        first_header = []
        for profit_center in profit_centers:
            first_header.append({'name': profit_center.name.upper(), 'style': 'text-align:right'})
            for route in routes[profit_center.id]:
                if len(routes[profit_center.id]) == 1:
                    first_header.append({'name': route, 'style': 'text-align:center', 'colspan': 2})
                    first_header.append({'name': routes[profit_center.id][route], 'style': 'text-align:right'})
                else:
                    first_header.append({'name': route, 'style': 'text-align:center', 'colspan': 3})
                    first_header.append({'name': routes[profit_center.id][route], 'style': 'text-align:right'})

        lines.append({
            'id': 'header',
            'name': '',
            'title_hover': 'Profit Center',
            'columns': first_header,
            'level': 1,
            'unfoldable': False,
            'colspan': 1,
            'style': 'text-align:left;font-size:14px;background-color:lightblue'
        })

        second_header = []
        for profit_center in profit_centers:
            second_header.append({'name': "{} TOTAAL".format(profit_center.name.upper()), 'style': 'text-align:right'})
            for route in routes[profit_center.id]:
                if len(routes[profit_center.id]) > 1:
                    second_header.append({'name': route, 'style': 'text-align:right'})
                second_header.append({'name': 'per enkel vlucht', 'style': 'text-align:right'})
                second_header.append({'name': 'per retour vlucht', 'style': 'text-align:right'})
                second_header.append({'name': 'per blok-uur', 'style': 'text-align:right'})

        lines.append({
            'id': 'header_date',
            'name': (parse(context.get('date_from')).strftime("(%B %Y T/M ") +
                     parse(context.get('date_to')).strftime("%B %Y) ")).upper(),
            'title_hover': '',
            'columns': second_header,
            'level': 1,
            'unfoldable': False,
            'colspan': 1,
            'style': 'font-size:14px;background-color:lightblue'
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
