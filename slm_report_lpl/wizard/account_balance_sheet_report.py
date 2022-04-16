# -*- coding: utf-8 -*-
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

import calendar
from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__)


class AccountLayoutBalanceSheetReport(models.TransientModel):
    _name = 'account.balancesheet.report'
    _inherit = "account.common.report"
    _description = 'Report Layout Balance sheet'

    @api.model
    def _get_account_report(self):
        reports = []
        if self._context.get('active_id'):
            menu = self.env['ir.ui.menu'].browse(
                self._context.get('active_id')).name
            reports = self.env['slm.financial.reports.define'].search(
                [('name', 'ilike', menu)])
        return reports and reports[0] or False

    @api.model
    def _get_dates(self):
        self.date_month_prior = self.date_to.replace(
            day=1) + relativedelta(days=-1)
        self.date_from_year_prior = self.date_from + relativedelta(months=-12)
        self.date_to_year_prior = self.date_to + relativedelta(months=-12)
        month_name = calendar.month_name[self.date_to.month]
        year = self.date_to.year
        self.col_text_1 = '%s %s' % (month_name[:3], year)
        year = self.date_to_year_prior.year
        self.col_text_2 = ' %s %s' % (month_name[:3], year)
        month_name = calendar.month_name[self.date_month_prior.month]
        year = self.date_month_prior.year
        self.col_text_3 = ' %s %s' % (month_name[:3], year)

    @api.model
    def _get_es_consolidate(self):
        self.es_consolidate = ('SLM CONSOLIDATED' ==
                               self.env.user.company_id.name)

    enable_filter = fields.Boolean(string='Filter?', default=False)
    account_report_id = fields.Many2one('slm.financial.reports.define', string='Financial Reports',
                                        required=True, default=_get_account_report, domain=[('type', '=', 'bls')])
    label_filter = fields.Char(
        string='Column Label', help="This label will be displayed on report to show the balance computed for the given comparison filter.")
    filter_cmp = fields.Selection([('filter_no', 'No Filters'), (
        'filter_date', 'Date')], string='Filter by', required=True, default='filter_no')
    date_from_cmp = fields.Date(string='Start Date')
    date_to_cmp = fields.Date(string='End Date')
    debit_credit = fields.Boolean(string='Display Debit/Credit Columns',
                                  help="This option allows you to get more details about the way your balances are computed. Because it is space consuming, we do not allow to use it while doing a comparison.")
    date_month_prior = fields.Date(
        compute='_get_dates', string='End Date Month Prior')
    date_from_year_prior = fields.Date(
        compute='_get_dates', string='End Date Year Prior')
    date_to_year_prior = fields.Date(
        compute='_get_dates', string='Start Date Year Prior')
    col_text_1 = fields.Char(compute='_get_dates')
    col_text_2 = fields.Char(compute='_get_dates')
    col_text_3 = fields.Char(compute='_get_dates')
    tag_id = fields.Many2one('slm.financial.reports.define.lines',
                             'Tags Reports', domain=[('type', '=', 'detail')])
    multi_company_ids = fields.Many2many('res.company', string="Company")
    enable_consolidate = fields.Boolean(string='Consolidated?', default=False)
    #detail_by_subgroup = fields.Boolean(string='Detail by subgroup?',default=True)
    es_consolidate = fields.Boolean(readonly=True)

    @api.model
    def default_get(self, fields):
        result = super(AccountLayoutBalanceSheetReport,
                       self).default_get(fields)
        selected_companies = self.env['res.company'].search([])
        selected_report = self.env['slm.financial.reports.define'].search(
            [('type', '=', 'bls')], limit=1)
        result.update({
            'account_report_id': selected_report and selected_report.id or False,
            'es_consolidate': ('SLM CONSOLIDATED' == self.env.user.company_id.name),
        })
        return result

    def companies(self, id_company):
        selected_companies = self.env['res.company'].search(
            [('parent_id', '=', id_company)]).ids
        if selected_companies:
            _logger.info('MULTI_COMPANY:%s' % selected_companies)
            for cia in selected_companies:
                compa = self.companies(cia)
                if compa:
                    for x in compa:
                        selected_companies.append(x)
        return selected_companies

    @api.onchange('company_id', 'enable_consolidate')
    def company_id_change(self):
        res = {}
        selected_companies = self.companies(self.company_id.id)
        _logger.info('COMPANY:%s' % selected_companies)
        if selected_companies:
            xcia = self.env['res.company'].search(
                [('id', '=', selected_companies)]).ids
            xcia.append(self.company_id.id)
            _logger.info('COMPANY:%s' % xcia)
            self.multi_company_ids = [(6, 0, xcia)]
        else:
            self.multi_company_ids = False

    @api.onchange('account_report_id')
    def account_report_id_change(self):
        res = {}
        domain = {'tag_id': [('type', '=', 'detail')]}
        if self.account_report_id:
            report_tag_ids = self.env['slm.financial.reports.define.lines'].search(
                [('report_id', '=', self.account_report_id.id)])
            filtro = [x.id for x in report_tag_ids]
            #domain = {'tag_id': [('id', 'in', filtro),('type','=','detail')]}
            domain = {'tag_id': [
                ('report_id', '=', self.account_report_id.id), ('type', '=', 'detail')]}
        return {'domain': domain}

    def _build_comparison_context(self, data):
        result = {}
        result['multi_company_ids'] = 'multi_company_ids' in data['form'] and data['form']['multi_company_ids'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        if data['form']['filter_cmp'] == 'filter_date':
            result['date_from'] = data['form']['date_from_cmp']
            result['date_to'] = data['form']['date_to_cmp']
            result['strict_range'] = True
        return result

    def _build_month_prior_context(self, data):
        result = {}
        result['multi_company_ids'] = 'multi_company_ids' in data['form'] and data['form']['multi_company_ids'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = self.date_from
        result['date_to'] = data['form']['date_month_prior']
        result['strict_range'] = True
        return result

    def _build_year_prior_context(self, data):
        result = {}
        result['multi_company_ids'] = 'multi_company_ids' in data['form'] and data['form']['multi_company_ids'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from_year_prior']
        result['date_to'] = data['form']['date_to_year_prior']
        result['strict_range'] = True
        return result

    def _rebuild_used_context(self, data, used_context):
        result = used_context
        result['multi_company_ids'] = 'multi_company_ids' in data['form'] and data['form']['multi_company_ids'] or False
        return result

    def check_report(self):
        context = self._context
        res = super(AccountLayoutBalanceSheetReport, self).check_report()
        data = {}
        data['form'] = self.read(['date_month_prior', 'date_from_year_prior', 'date_to_year_prior', 'account_report_id', 'date_from_cmp',
                                  'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move', 'enable_consolidate', 'multi_company_ids'])[0]
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        month_prior_context = self._build_month_prior_context(data)
        year_prior_context = self._build_year_prior_context(data)
        used_context = self._rebuild_used_context(
            data, res['data']['form']['used_context'])
        if context.get('xls_export'):
            res['data']['form']['comparison_context'] = comparison_context
            res['data']['form']['month_prior_context'] = month_prior_context
            res['data']['form']['year_prior_context'] = year_prior_context
            res['data']['form']['used_context'] = used_context
        else:
            res['data']['form']['comparison_context'] = comparison_context
            res['data']['form']['month_prior_context'] = month_prior_context
            res['data']['form']['year_prior_context'] = year_prior_context
            res['data']['form']['used_context'] = used_context

        return res

    def _print_report(self, data):
        context = self._context
        data['form'].update(self.read(['tag_id', 'col_text_1', 'col_text_2', 'col_text_3', 'date_from_cmp', 'debit_credit', 'date_to_cmp',
                                       'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move', 'enable_consolidate', 'multi_company_ids'])[0])
        if context.get('xls_export'):
            return self.env.ref('slm_report_lpl.action_balancesheet_xls').report_action(self, data=data, config=False)
        return self.env.ref('slm_report_lpl.action_balancesheet').report_action(self, data=data, config=False)
