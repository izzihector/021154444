# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import logging

_logger = logging.getLogger(__name__)


class SlmFinancialReportsDefine(models.Model):
    _name = 'slm.financial.reports.define'
    _description = 'Define Structure for Financial Reports'

    name = fields.Char('Name report')
    description = fields.Text('Description')
    report_line = fields.One2many('slm.financial.reports.define.lines',
                                  'report_id', string='Report Lines', copy=True, auto_join=True)
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    type = fields.Selection([
        ('pyl', 'Proift & Loss'),
        ('bls', 'Balance Sheet')], string='Type', default='pyl')

    def _get_children_by_order(self):
        '''returns a recordset of all the children computed recursively, and sorted by sequence. Ready for the printing'''
        res = self
        children = self.search(
            [('parent_id', 'in', self.ids)], order='sequence ASC')
        if children:
            for child in children:
                res += child._get_children_by_order()
        return res

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
        # self.env['res.company'].search([('id','=',1)],limit=1)
        base_current = self.env.user.company_id
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
            currency = company_current.currency_id
            company_currency = cur.currency_id
            if company_currency == company_current.currency_id:
                rate = 1
            else:
                rate = company_currency._convert(
                    1, currency, cur, date_to, round=False)
                base_cur = 1
                rate_cur = base_current.currency_id._convert(
                    1, cur.currency_id, cur, date_to, round=False)
                rate_cia = base_current.currency_id._convert(
                    1, company_current.currency_id, cur, date_to, round=False)
                rate = company_currency._convert(
                    base_cur, currency, base_current, date_to, round=False)
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
                request = "SELECT account_id as id, to_char(date(account_move_line.date),'YYYY-MM') as year_month, " + ', '.join(mapping.values()) + \
                    " FROM " + tables + \
                    " WHERE account_id IN %s " \
                    + filters + \
                    " GROUP BY account_id, to_char(date(account_move_line.date),'YYYY-MM')"

                params = (tuple(accounts._ids),) + tuple(where_params)
                self.env.cr.execute(request, params)
                for row in self.env.cr.dictfetchall():
                    if res[row['id']]:
                        date_str = row['year_month']+'-01'
                        year = int(date_str[:4])
                        month = int(date_str[5:7])
                        date_rate = (datetime.date(year + month//12, month %
                                                   12 + 1, 1) - datetime.timedelta(days=1))
                        if company_currency == company_current.currency_id:
                            rate = 1
                        else:
                            rate = company_currency._convert(
                                1, currency, cur, date_to, round=False)
                            base_cur = 1
                            rate_cur = base_current.currency_id._convert(
                                1, cur.currency_id, cur, date_rate, round=False)
                            rate_cia = base_current.currency_id._convert(
                                1, company_current.currency_id, cur, date_rate, round=False)
                            rate = company_currency._convert(
                                base_cur, currency, base_current, date_rate, round=False)
                        res[row['id']]['credit'] = res[row['id']
                                                       ]['credit'] + row['credit']*rate
                        res[row['id']]['debit'] = res[row['id']
                                                      ]['debit'] + row['debit']*rate
                        res[row['id']]['balance'] = res[row['id']
                                                        ]['balance'] + row['balance']*rate
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
                request = "SELECT account_id as id, to_char(date(account_move_line.date),'YYYY-MM') as year_month, " + ', '.join(mapping.values()) + \
                    " FROM " + tables + \
                    " WHERE account_id IN %s " \
                    + filters + \
                    " GROUP BY account_id, to_char(date(account_move_line.date),'YYYY-MM')"
                params = (tuple(accounts._ids),) + tuple(where_params)
                self.env.cr.execute(request, params)
                for row in self.env.cr.dictfetchall():
                    if res[row['id']]:
                        date_str = row['year_month']+'-01'
                        year = int(date_str[:4])
                        month = int(date_str[5:7])
                        date_rate = (datetime.date(year + month//12, month %
                                                   12 + 1, 1) - datetime.timedelta(days=1))
                        if company_currency == company_current.currency_id:
                            rate = 1
                        else:
                            rate = company_currency._convert(
                                1, currency, cur, date_to, round=False)
                            base_cur = 1
                            rate_cur = base_current.currency_id._convert(
                                1, cur.currency_id, cur, date_rate, round=False)
                            rate_cia = base_current.currency_id._convert(
                                1, company_current.currency_id, cur, date_rate, round=False)
                            rate = company_currency._convert(
                                base_cur, currency, base_current, date_rate, round=False)
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
        id_vacio = 0
        for account in accounts:
            account_id = account_obj.search([('id', '=', account)])
            sg_id = account_id.subgroup_id and account_id.subgroup_id.id or id_vacio
            sg_id = account_id.subgroup_id.id
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
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            res[report.id]['name'] = report.name
            res[report.id]['type'] = report.type
            res[report.id]['code'] = report.code
            if report.type == 'detail':
                filtro = []
                account_ids = []
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
            elif report.formula:
                safe_eval(report.formula, localdict, mode='exec', nocopy=True)
                res[report.id]['balance'] = float(localdict['result'])
            else:
                res[report.id]['balance'] = 0.00
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

    def get_renglon(self, report_name, renglon_code):
        context = self._context
        date_to = context.get('date_to')
        _logger.info('date_to: %s', date_to)
        result = 0
        define_id = self.env['slm.financial.reports.define'].search(
            [('name', '=', report_name)], limit=1)
        if define_id:
            report_res = define_id._compute_report_balance(
                define_id.report_line)
            _logger.info(
                '*****************///////////////////// >>>>>>>>>report_res: %s', report_res)
            for res in report_res:
                if date_to >= '2019-07-31':
                    _logger.info(
                        'res: %s', (report_res[res]['code'], report_res[res]['name'], report_res[res]['balance']))
                if report_res[res]['code'] == renglon_code:
                    result = report_res[res]['balance']
        return result


class SlmDefineFinancialReportsLinesDefine(models.Model):
    _name = 'slm.financial.reports.define.lines'
    _description = 'Define Financial report structure lines'
    _order = 'sequence'

    """
    @api.depends('sequence')
    def _is_primary(self):
        return self.sequence==1
        """

    report_id = fields.Many2one('slm.financial.reports.define', string='Report Reference',
                                required=True, ondelete='cascade', index=True, copy=False, readonly=True)
    name = fields.Char(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    code = fields.Char('Code', size=5)
    type = fields.Selection([
        ('detail', 'Detail'),
        ('tittle', 'Tittle')], string='Type', default='detail')
    tag_ids = fields.Many2many('account.account.tag', string='Account Tags')
    formula = fields.Text('Formula')
    sign = fields.Char('Sign', size=1)
    primary = fields.Boolean('Base para Calculo')
    group_ids = fields.Many2many('account.group', string='Account Groups')
    subgroup_ids = fields.Many2many(
        'account.subgroup', string='Account Subgroups')
    reverse_order = fields.Boolean('Reverse order', default=False)

    def _compute_formula(self, localdict):
        self.ensure_one()
        if self.type == 'titlle' and self.formula:
            _logger.info('formula: %s', self.formula)
            safe_eval(self.formula, localdict, mode='exec', nocopy=True)
            return (float(localdict['result']) if localdict['result'] else 0.00)
        return 0.00
