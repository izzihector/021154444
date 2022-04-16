# -*- coding: utf-8 -*-

from odoo import models


class report_account_coa(models.AbstractModel):
    _inherit = "account.coa.report"
    # _inherit = "account.report"

    def _do_query_group_by_account(self, options, line_id):
        results = self._do_query(options, line_id, group_by_account=True, limit=False)

        def build_converter(currency):
            def convert(amount):
                return amount
            return convert

        compute_table = {
            a.id: build_converter(a.company_id.currency_id)
            for a in self.env['account.account'].browse([k[0] for k in results])
        }
        results = dict([(
            k[0], {
                'balance': compute_table[k[0]](k[1]) if k[0] in compute_table else k[1],
                'amount_currency': k[2],
                'debit': compute_table[k[0]](k[3]) if k[0] in compute_table else k[3],
                'credit': compute_table[k[0]](k[4]) if k[0] in compute_table else k[4],
            }
        ) for k in results])
        return results

    def _do_query(self, options, line_id, group_by_account=True, limit=False):
        if group_by_account:
            select = "SELECT \"account_move_line\".account_id"

            if self.env.user.company_id.currency_id.id == 2:
                select += """,COALESCE(SUM(("account_move_line".debit-"account_move_line".credit) /
                      (CASE WHEN "account_move_line".company_currency_id = 2 THEN 1 ELSE "res_currency_rate".rate END)), 0),
                      COALESCE(SUM("account_move_line".amount_currency /
                      (CASE WHEN "account_move_line".company_currency_id = 2 THEN 1 ELSE "res_currency_rate".rate END)), 0),
                      COALESCE(SUM("account_move_line".debit /
                      (CASE WHEN "account_move_line".company_currency_id = 2 THEN 1 ELSE "res_currency_rate".rate END)), 0),
                      COALESCE(SUM("account_move_line".credit /
                      (CASE WHEN "account_move_line".company_currency_id = 2 THEN 1 ELSE "res_currency_rate".rate END)), 0)
                      """
            else:
                select += """,COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0),
                          SUM("account_move_line".amount_currency),
                          SUM("account_move_line".debit),
                          SUM("account_move_line".credit)
                          """

            if options.get('cash_basis'):
                select = select.replace('debit', 'debit_cash_basis').replace(
                    'credit', 'credit_cash_basis').replace('balance', 'balance_cash_basis')
        else:
            select = "SELECT \"account_move_line\".id"
        sql = "%s FROM %s "
        if self.env.user.company_id.currency_id.id == 2:
            join = """LEFT JOIN "res_currency_rate" ON ("account_move_line".company_currency_id = "res_currency_rate".currency_id AND "res_currency_rate".name = date_trunc('month', "account_move_line".date)::date) """
        else:
            join = ""

        where = "WHERE %s%s"
        sql += join + where
        if group_by_account:
            sql += "GROUP BY \"account_move_line\".account_id"
        else:
            sql += " GROUP BY \"account_move_line\".id"
            sql += " ORDER BY MAX(\"account_move_line\".date),\"account_move_line\".id"
            if limit and isinstance(limit, int):
                sql += " LIMIT " + str(limit)
        user_types = self.env['account.account.type'].search(
            [('type', 'in', ('receivable', 'payable'))])
        with_sql, with_params = self._get_with_statement(user_types)
        tables, where_clause, where_params = self.env['account.move.line']._query_get(
        )
        line_clause = line_id and ' AND \"account_move_line\".account_id = ' + \
            str(line_id) or ''
        query = sql % (select, tables, where_clause, line_clause)
        self.env.cr.execute(with_sql + query, with_params + where_params)
        results = self.env.cr.fetchall()
        return results
