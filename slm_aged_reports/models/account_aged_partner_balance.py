# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.tools.misc import format_date


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_accounts = None


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"

    def _set_context(self, options):
        ctx = super(ReportAccountAgedPartner, self)._set_context(options)
        accounts = []
        if options.get('accounts'):
            accounts = [c.get('id')
                        for c in options['accounts'] if c.get('selected')]
            accounts = accounts if len(accounts) > 0 else [
                c.get('id') for c in options['accounts']]
        ctx['accounts'] = len(accounts) > 0 and accounts
        return ctx

    def _get_options(self, previous_options=None):
        if not previous_options:
            previous_options = {}
        options = super(ReportAccountAgedPartner,
                        self)._get_options(previous_options)
        companies = options.get('multi_company')
        options['accounts'] = self._get_options_accounts(
                companies=companies)
        # Merge old options with default from this report
        for key, value in options.items():
            if key in previous_options and value is not None and previous_options[key] is not None:
                if key == 'accounts':
                    for index, account in enumerate(options[key]):
                        selected_account = next((previous_option for previous_option in previous_options[key]
                                                 if previous_option['id'] == account['id']), None)
                        if selected_account:
                            options[key][index] = selected_account
        return options

    def _get_options_accounts(self, account_type=None, companies=None):
        domain = [('internal_type', '=', account_type)]
        if companies:
            company_ids = [c.get('id') for c in companies if c.get('selected')]
            if company_ids:
                domain.append(('company_id', 'in', company_ids))
        accounts = self.env['account.account'].search(domain)
        return [{'id': c.id, 'name': "{} {}".format(c.code, c.name), 'selected': False} for c in accounts]


class ReportAccountAgedReceivable(models.AbstractModel):
    _inherit = "account.aged.receivable"

    def _get_options_accounts(self, account_type='receivable', companies=None):
        return super(ReportAccountAgedReceivable, self)._get_options_accounts(account_type, companies)


class ReportAccountAgedPayable(models.AbstractModel):
    _inherit = "account.aged.payable"

    def _get_options_accounts(self, account_type='payable', companies=None):
        return super(ReportAccountAgedPayable, self)._get_options_accounts(account_type, companies)
