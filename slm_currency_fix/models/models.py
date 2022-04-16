# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    def _get_currency_table(self):
        used_currency = self.env.user.company_id.currency_id.with_context(
            company_id=self.env.user.company_id.id)
        currency_table = {}
        for company in self.env['res.company'].search([]):
            if company.currency_id != used_currency:
                # currency_table[company.currency_id.id] = used_currency.rate / company.currency_id.rate
                currency_table[company.currency_id.id] = 1
        return currency_table


class Currency(models.Model):
    _inherit = "res.currency"

    def get_rate_by_date(self, date):
        print(date, self.id)


class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    def _query_get_select_sum(self, currency_table):
        """ Little function to help building the SELECT statement when computing the report lines.

            @param currency_table: dictionary containing the foreign currencies (key) and their factor (value)
                compared to the current user's company currency
            @returns: the string and parameters to use for the SELECT
        """
        extra_params = []
        select = '''
            COALESCE(SUM(\"account_move_line\".balance), 0) AS balance,
            COALESCE(SUM(\"account_move_line\".amount_residual), 0) AS amount_residual,
            COALESCE(SUM(\"account_move_line\".debit), 0) AS debit,
            COALESCE(SUM(\"account_move_line\".credit), 0) AS credit
        '''
        if currency_table:
            select = '''
            COALESCE (SUM(balance / (CASE WHEN "account_move_line".company_currency_id = 2 THEN 1 ELSE RCR.rate END)), 
                0) AS balance, 
            COALESCE (SUM(amount_residual / 
                (CASE WHEN "account_move_line".company_currency_id = 2 THEN 1 ELSE RCR.rate END)), 0) 
                AS amount_residual, 
            COALESCE (SUM(debit / (CASE WHEN "account_move_line".company_currency_id = 2 THEN 1 ELSE RCR.rate END)), 0) 
                AS debit, 
            COALESCE (SUM(credit / (CASE WHEN "account_move_line".company_currency_id = 2 THEN 1 ELSE RCR.rate END)), 0)
                AS credit
            '''

        if self.env.context.get('cash_basis'):
            for field in ['debit', 'credit', 'balance']:
                # replace the columns selected but not the final column name (... AS <field>)
                number_of_occurence = len(select.split(field)) - 1
                select = select.replace(
                    field, field + '_cash_basis', number_of_occurence - 1)
        return select, extra_params
