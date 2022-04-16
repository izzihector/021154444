# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

import logging

_logger = logging.getLogger(__name__)


class ReportLayoutProfitLoss(models.AbstractModel):
    _name = 'report.slm_report_lpl.report_layoutprofitloss'

    def _compute_account_balance(self, accounts2, filtro_origen):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        context = self._context
        company_id = context.get('company_id')
        date_to = context.get('date_to')
        company_current = self.env['res.company'].search(
            [('id', '=', company_id)], limit=1)
        multi_company_ids = context.get('multi_company_ids')
        filtro = filtro_origen
        res = {}
        if multi_company_ids:
            companies = self.env['res.company'].search(
                [('id', 'in', multi_company_ids)])
        else:
            companies = self.env['res.company'].search(
                [('id', '=', company_id)])
        for cur in companies:
            filtro = filtro_origen.copy()
            filtro.append(('company_id', '=', cur.id))
            _logger.info('************* company *************:%s' % cur.name)
            _logger.info('------------- filtro --------------:%s' % filtro)
            currency = company_current.currency_id
            company_currency = cur.currency_id
            if company_currency == company_current.currency_id:
                rate = 1
            else:
                rate = company_currency._convert(
                    1, currency, cur, date_to, round=False)
            _logger.info('////// Tasa ////////:(%s) %s / %s = %s' % (date_to,
                                                                     company_current.currency_id.name, company_currency.name, rate))
            accounts = self.env['account.account'].search(filtro)
            for account in accounts:
                res[account.id] = dict.fromkeys(mapping, 0.0)
            if accounts:
                tables, where_clause, where_params = self.env['account.move.line'].with_context(
                    company_id=cur.id)._query_get()
                tables = tables.replace(
                    '"', '') if tables else "account_move_line"
                wheres = [""]

                if where_clause.strip():
                    wheres.append(where_clause.strip())

                filters = " AND ".join(wheres)
                request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                    " FROM " + tables + \
                    " WHERE account_id IN %s " \
                    + filters + \
                    " GROUP BY account_id"

                params = (tuple(accounts._ids),) + tuple(where_params)
                self.env.cr.execute(request, params)
                for row in self.env.cr.dictfetchall():
                    if res[row['id']]:
                        currency = company_current.currency_id.with_context(
                            date=date_to)
                        company_currency = cur.currency_id
                        if company_currency == currency:
                            rate = 1
                        else:
                            rate = currency.compute(1, company_currency)
                        res[row['id']]['credit'] = res[row['id']
                                                       ]['credit'] + row['credit']/rate
                        res[row['id']]['debit'] = res[row['id']
                                                      ]['debit'] + row['debit']/rate
                        res[row['id']]['balance'] = res[row['id']
                                                        ]['balance'] + row['balance']/rate
                    else:
                        res[row.pop('id')].append(row)

                tables, where_clause, where_params = self.env['account.move.line'].with_context(
                    company_id=cur.id, initial_bal=True)._query_get()
                tables = tables.replace(
                    '"', '') if tables else "account_move_line"
                wheres = [""]
                if where_clause.strip():
                    wheres.append(where_clause.strip())
                filters = " AND ".join(wheres)
                request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                    " FROM " + tables + \
                    " WHERE account_id IN %s " \
                    + filters + \
                    " GROUP BY account_id"
                params = (tuple(accounts._ids),) + tuple(where_params)
                self.env.cr.execute(request, params)
                for row in self.env.cr.dictfetchall():
                    if res[row['id']]:
                        currency = company_current.currency_id.with_context(
                            date=date_to)
                        company_currency = cur.currency_id
                        if company_currency == currency:
                            rate = 1
                        else:
                            rate = currency.compute(1, company_currency)
                        res[row['id']]['credit'] = res[row['id']
                                                       ]['credit'] + row['credit']*rate
                        res[row['id']]['debit'] = res[row['id']
                                                      ]['debit'] + row['debit']*rate
                        res[row['id']]['balance'] = res[row['id']
                                                        ]['balance'] + row['balance']*rate
                    else:
                        res[row.pop('id')].append(row)
        return res

    def _compute_subgroup_balance(self, accounts):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        fields = ['credit', 'debit', 'balance']
        account_obj = self.env['account.account']
        id_vacio = 999999
        for account in accounts:
            account_id = account_obj.search([('id', '=', account)])
            sg_id = account_id.subgroup_id and account_id.subgroup_id.id or id_vacio
            res[sg_id] = dict.fromkeys(mapping, 0.0)
        for account in accounts:
            account_id = account_obj.search([('id', '=', account)])
            sg_id = account_id.subgroup_id and account_id.subgroup_id.id or id_vacio
            for field in fields:
                res[sg_id][field] += accounts[account][field]
        return res

    def _compute_report_balance(self, reports):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance']

        localdict = {}
        localdict['result'] = 0.00
        for report in reports:
            localdict['report'] = report.report_id.with_context(self._context)
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            res[report.id]['name'] = report.name
            res[report.id]['type'] = report.type
            if report.type == 'detail':
                # it's the sum of the linked accounts
                #account_ids = [x.account_ids for x in report.tag_ids]
                filtro = []
                account_ids = []
                """
                for tag in report.tag_ids:
                    if tag.account_ids:
                        for account in tag.account_ids:
                            account_ids.append(account.id)
                filtro.append(('id','in',account_ids))
                """
                if report.tag_ids:
                    filtro.append(('tag_ids', 'in', report.tag_ids.ids))
                if report.group_ids:
                    filtro.append(('group_id', 'in', report.group_ids.ids))
                if report.subgroup_ids:
                    filtro.append(
                        ('subgroup_id', 'in', report.subgroup_ids.ids))
                list_ids = self.env['account.account'].search(filtro)
                res[report.id]['account'] = self._compute_account_balance(
                    list_ids, filtro)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
                res[report.id]['subgroup'] = self._compute_subgroup_balance(
                    res[report.id]['account'])
            else:
                safe_eval(report.formula, localdict, mode='exec', nocopy=True)
                res[report.id]['balance'] = float(localdict['result'])
            if report.sign and report.sign in ['+', '-']:
                rep_sing = 1.00
                if report.sign in ['-']:
                    rep_sing = -1.00
                res[report.id]['balance'] = abs(
                    res[report.id]['balance']) * rep_sing
                for subgroup in res[report.id]['subgroup']:
                    res[report.id]['subgroup'][subgroup]['balance'] = abs(
                        res[report.id]['subgroup'][subgroup]['balance']) * rep_sing
            localdict[report.code] = res[report.id]['balance']
        return res

    def get_account_lines(self, data):
        lines = []
        account_report = self.env['slm.financial.reports.define'].search(
            [('id', '=', data['account_report_id'][0])])
        #child_reports = account_report._get_children_by_order()
        tag_id = data['tag_id'] and data['tag_id'][0] or False
        if tag_id:
            child_reports = account_report.report_line.filtered(
                lambda l: l.id == tag_id)
        else:
            child_reports = account_report.report_line
        res = self.with_context(data.get('used_context')
                                )._compute_report_balance(child_reports)
        comparison_res = self.with_context(
            data.get('year_prior_context'))._compute_report_balance(child_reports)
        for report_id, value in comparison_res.items():
            res[report_id]['year_prior_bal'] = value['balance']
            if tag_id:
                res[report_id]['year_prior_subgroup'] = value['subgroup']
        comparison_res = self.with_context(
            data.get('month_prior_context'))._compute_report_balance(child_reports)
        for report_id, value in comparison_res.items():
            res[report_id]['month_prior_bal'] = value['balance']
            if tag_id:
                res[report_id]['month_prior_subgroup'] = value['subgroup']

        incomes = 0.00
        incomes_budget = 0.00
        incomes_year_prior_bal = 0.00
        incomes_month_prior_bal = 0.00
        new_context = {}
        if tag_id:
            for report in child_reports:
                vals = {
                    'name': report.name,
                    'balance': 0.00,
                    'type': 'tag',
                    'level': 1,
                    'account_type': False,  # used to underline the financial report balances
                    'budget': 0.00,
                    'balance_cmp': 0.00,
                    'year_prior_bal': 0.00,
                    'month_prior_bal': 0.00,
                    'diff_budget': 0.00,
                    'diff_year': 0.00,
                    'diff_month': 0.00,
                    'percent_balance': 0.00,
                    'percent_budget': 0.00,
                    'percent_year_prior_bal': 0.00,
                    'percent_month_prior_bal': 0.00,
                    'percent_diff_budget': 0.00,
                    'percent_diff_year': 0.00,
                    'percent_diff_month': 0.00
                }
                lines.append(vals)
                subgroup_bal = res[report.id]['subgroup']
                year_prior_subgroup = res[report.id]['year_prior_subgroup']
                month_prior_subgroup = res[report.id]['month_prior_subgroup']
                incomes = sum([subgroup_bal[x]['balance']
                               for x in subgroup_bal])
                incomes_budget = 0.00
                incomes_year_prior_bal = sum(
                    [year_prior_subgroup[x]['balance'] for x in year_prior_subgroup])
                incomes_month_prior_bal = sum(
                    [month_prior_subgroup[x]['balance'] for x in month_prior_subgroup])
                subgroup_obj = self.env['account.subgroup'].search([])
                sg_max = len(subgroup_obj)
                sg_actual = 0
                for record in subgroup_obj:
                    sg_actual += 1
                    if sg_actual == sg_max:
                        cursor = {1, 2}
                    else:
                        cursor = {1}
                    for x in cursor:
                        if x == 1:
                            sg_name = record.name
                            sg_id = record.id
                            sg_sing = report.sign
                            sg_formula = report.formula
                        else:
                            sg_name = _('It has no associated subgroup')
                            sg_id = 999999
                            sg_sing = ' '
                            sg_formula = report.formula
                        if (sg_id in subgroup_bal) or (sg_id in year_prior_subgroup) or (sg_id in month_prior_subgroup):
                            rep_sing = 1
                            if sg_sing and sg_sing == '-':
                                rep_sing = -1
                            vals = {
                                'name': sg_name,
                                'balance': 0.00,
                                'type': 'detail',
                                'level': 1,
                                'account_type': False,  # used to underline the financial report balances
                                'budget': 0.00,
                                'balance_cmp': 0.00,
                                'year_prior_bal': 0.00,
                                'month_prior_bal': 0.00,
                                'diff_budget': 0.00,
                                'diff_year': 0.00,
                                'diff_month': 0.00,
                                'percent_balance': 0.00,
                                'percent_budget': 0.00,
                                'percent_year_prior_bal': 0.00,
                                'percent_month_prior_bal': 0.00,
                                'percent_diff_budget': 0.00,
                                'percent_diff_year': 0.00,
                                'percent_diff_month': 0.00
                            }
                            if sg_id in subgroup_bal:
                                vals['balance'] = (
                                    subgroup_bal[sg_id]['balance'] if subgroup_bal[sg_id]['balance'] else 0.00)
                            if sg_id in year_prior_subgroup:
                                vals['year_prior_bal'] = (
                                    year_prior_subgroup[sg_id]['balance'] if year_prior_subgroup[sg_id]['balance'] else 0.00)
                            if sg_id in month_prior_subgroup:
                                vals['month_prior_bal'] = (
                                    month_prior_subgroup[sg_id]['balance'] if month_prior_subgroup[sg_id]['balance'] else 0.00)

                            vals['diff_budget'] = vals['balance'] - \
                                vals['budget']
                            vals['diff_year'] = vals['balance'] - \
                                vals['year_prior_bal']
                            vals['diff_month'] = vals['balance'] - \
                                vals['month_prior_bal']

                            vals['percent_balance'] = (
                                vals['balance']/incomes * 100 if incomes else 0.00)
                            vals['percent_budget'] = (
                                vals['budget']/incomes_budget * 100 if incomes_budget else 0.00)
                            vals['percent_year_prior_bal'] = (
                                vals['year_prior_bal']/incomes_year_prior_bal * 100 if incomes_year_prior_bal else 0.00)
                            vals['percent_month_prior_bal'] = (
                                vals['month_prior_bal']/incomes_month_prior_bal * 100 if incomes_month_prior_bal else 0.00)

                            vals['percent_diff_budget'] = (
                                vals['diff_budget']/vals['budget'] * 100 if vals['budget'] else 0.00)
                            vals['percent_diff_year'] = (
                                vals['diff_year']/vals['year_prior_bal'] * 100 if vals['year_prior_bal'] else 0.00)
                            vals['percent_diff_month'] = (
                                vals['diff_month']/vals['month_prior_bal'] * 100 if vals['month_prior_bal'] else 0.00)

                            lines.append(vals)

        else:
            for report in child_reports:
                rep_sing = 1
                if report.sign and report.sign == '-':
                    rep_sing = -1
                vals = {
                    'name': report.name,
                    'balance': (res[report.id]['balance'] if res[report.id]['balance'] else 0.00),
                    'type': report.type,
                    'level': 1,
                    # used to underline the financial report balances
                    'account_type': report.type or False,
                    'budget': 0.00,
                }
                if not incomes:
                    incomes = vals['balance']

                if data['debit_credit']:
                    vals['debit'] = res[report.id]['debit']
                    vals['credit'] = res[report.id]['credit']

                if data['enable_filter']:
                    vals['balance_cmp'] = res[report.id]['comp_bal']

                if 1 == 1:
                    vals['year_prior_bal'] = res[report.id]['year_prior_bal']
                    vals['month_prior_bal'] = res[report.id]['month_prior_bal']
                else:
                    vals['year_prior_bal'] = 0.00
                    vals['month_prior_bal'] = 0.00

                vals['diff_budget'] = vals['balance'] - vals['budget']
                vals['diff_year'] = vals['balance'] - vals['year_prior_bal']
                vals['diff_month'] = vals['balance'] - vals['month_prior_bal']

                if not incomes:
                    incomes = vals['balance']
                    incomes_budget = vals['budget']
                    incomes_year_prior_bal = vals['year_prior_bal']
                    incomes_month_prior_bal = vals['month_prior_bal']

                vals['percent_balance'] = (
                    vals['balance']/incomes * 100 if incomes else 0.00)
                vals['percent_budget'] = (
                    vals['budget']/incomes_budget * 100 if incomes_budget else 0.00)
                vals['percent_year_prior_bal'] = (
                    vals['year_prior_bal']/incomes_year_prior_bal * 100 if incomes_year_prior_bal else 0.00)
                vals['percent_month_prior_bal'] = (
                    vals['month_prior_bal']/incomes_month_prior_bal * 100 if incomes_month_prior_bal else 0.00)

                vals['percent_diff_budget'] = (
                    vals['diff_budget']/vals['budget'] * 100 if vals['budget'] else 0.00)
                vals['percent_diff_year'] = (
                    vals['diff_year']/vals['year_prior_bal'] * 100 if vals['year_prior_bal'] else 0.00)
                vals['percent_diff_month'] = (
                    vals['diff_month']/vals['month_prior_bal'] * 100 if vals['month_prior_bal'] else 0.00)

                lines.append(vals)

        return lines

    def company_tittle(self, book):
        result = book.company_id.name
        if book.enable_consolidate:
            result = ''
            for rec in book.company_ids:
                if result:
                    result += '/ '
                # self.env['res.company'].search([('id','=',rec)],limit=1).name
                result += rec.name
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_lines = self.get_account_lines(data.get('form'))
        report_name = docs.account_report_id.name
        if data['form'].get('tag_id', False):
            report_name = "%s (subgroup)" % report_name
        if data['form'].get('enable_consolidate', False):
            report_name = "%s - CONSOLIDATE" % report_name
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'tittle': report_name,
            'get_account_lines': report_lines,
        }
