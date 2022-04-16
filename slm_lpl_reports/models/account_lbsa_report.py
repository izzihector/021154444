# -*- coding: utf-8 -*-

import collections
import re
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class AccountLBSAReport(models.AbstractModel):
    _name = "account.lbsa.report"
    _description = "Layout Balance Sheet (ACTIVA)"
    _inherit = "account.lpl.report"

    @api.model
    def _get_report_name(self):
        return _("Layout Balance Sheet (ACTIVA)")

    def _get_tags(self, report_id=2):
        return super(AccountLBSAReport, self)._get_tags(report_id)

    def _do_query_lpl(self, date_from=None, date_to=None, report_id=2, balance=True):
        return super(AccountLBSAReport, self)._do_query_lpl(date_from, date_to, report_id, balance)

    def _do_query_lpl_budget(self, date_from=None, date_to=None, report_id=2, balance=True):
        return super(AccountLBSAReport, self)._do_query_lpl_budget(date_from, date_to, report_id, balance)

    def _do_query_lpl_tag(self, tag_id, context, date_from=None, date_to=None, order='DESC', report_id=2, balance=True):
        return super(AccountLBSAReport, self)._do_query_lpl_tag(tag_id, context, date_from, date_to, order, report_id,
                                                                balance)

    def _do_query_lpl_budget_tag(self, tag_id, context, date_from=None, date_to=None, order='DESC', report_id=2, balance=True):
        return super(AccountLBSAReport, self)._do_query_lpl_budget_tag(tag_id, context, date_from, date_to, order,
                                                                       report_id, balance)

    def _get_lines_lpl(self, lines, last_day_last_month, date_last_year, use_total=True):
        return super(AccountLBSAReport, self)._get_lines_lpl(lines, last_day_last_month, date_last_year, use_total)

    def _get_lines_lpl_notes(self, lines, context, last_day_last_month, date_last_year):
        return super(AccountLBSAReport, self)._get_lines_lpl_notes(lines, context, last_day_last_month, date_last_year)