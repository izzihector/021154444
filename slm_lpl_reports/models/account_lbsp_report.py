# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class AccountLBSPReport(models.AbstractModel):
    _name = "account.lbsp.report"
    _description = "Layout Balance Sheet (Passiva)"
    _inherit = "account.lpl.report"

    @api.model
    def _get_report_name(self):
        return _("Layout Balance Sheet (Passiva)")

    def _get_tags(self, report_id=5):
        return super(AccountLBSPReport, self)._get_tags(report_id)

    def _do_query_lpl(self, date_from=None, date_to=None, report_id=5, balance=True):
        return super(AccountLBSPReport, self)._do_query_lpl(date_from, date_to, report_id, balance)

    def _do_query_lpl_budget(self, date_from=None, date_to=None, report_id=5, balance=True):
        return super(AccountLBSPReport, self)._do_query_lpl_budget(date_from, date_to, report_id, balance)

    def _do_query_lpl_tag(self, tag_id, context, date_from=None, date_to=None, order='DESC', report_id=5, balance=True):
        return super(AccountLBSPReport, self)._do_query_lpl_tag(tag_id, context, date_from, date_to, order, report_id,
                                                                balance)

    def _do_query_lpl_budget_tag(self, tag_id, context, date_from=None, date_to=None, order='DESC', report_id=5,
                                 balance=True):
        return super(AccountLBSPReport, self)._do_query_lpl_budget_tag(tag_id, context, date_from, date_to, order,
                                                                       report_id, balance)

    def _get_lpl_results(self, date_to=None, budget=False):
        if budget:
            results = self._do_query_lpl_budget(date_to=date_to, report_id=1)
        else:
            results = self._do_query_lpl(date_to=date_to, report_id=1)
        results_by_code = {result['code']: result['balance'] for result in results}
        results_by_code['result'] = 0
        for i, result in enumerate(results):
            if result['type'] == 'tittle' and result['formula']:
                safe_eval(result['formula'], results_by_code, mode='exec', nocopy=True)
                results_by_code[result['code']] = results_by_code['result']
                results[i]['balance'] = results_by_code['result']
            elif result['type'] == 'tittle':
                results[i]['type'] = 'header'
        return results[-1]['balance']

    def _get_lines_lpl(self, lines, last_day_last_month, date_last_year, use_total=True):
        return super(AccountLBSPReport, self)._get_lines_lpl(lines, last_day_last_month, date_last_year, use_total)

    def _get_lines_lpl_notes(self, lines, context, last_day_last_month, date_last_year):
        return super(AccountLBSPReport, self)._get_lines_lpl_notes(lines, context, date_last_year, last_day_last_month)