# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Saritha Sahadevan(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################
#from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo import fields
import datetime
from time import gmtime, strftime
from odoo import _
from odoo.tools.safe_eval import safe_eval
from io import BytesIO

from odoo import models
import logging
from operator import itemgetter


_logger = logging.getLogger(__name__)


class ReportLayoutProfitLossXls(models.AbstractModel):

    _name = 'report.slm_report_lpl.report_layoutprofitloss.xlsx'
    _inherit = 'report.report_xlsx.abstract'

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
        # company_current = self.env['res.company']._company_default_get(
        #     'account')
        company_current = self.env.company
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
            #_logger.info('************* company *************:%s'%cur.name)
            #_logger.info('------------- filtro --------------:%s'%filtro)
            currency = company_current.currency_id
            company_currency = cur.currency_id
            if company_currency == company_current.currency_id:
                rate = 1
            else:
                base_cur = 1
                rate_cur = base_current.currency_id._convert(
                    1, cur.currency_id, cur, date_to, round=False)
                rate_cia = base_current.currency_id._convert(
                    1, company_current.currency_id, cur, date_to, round=False)
                rate = company_currency._convert(
                    base_cur, currency, base_current, date_to, round=False)
                # rate = rate_cia/rate_cur #company_currency._convert(base_cur, base_current.currency_id, base_current, date_to, round=False)
            rate_cur = base_current.currency_id._convert(
                1, cur.currency_id, cur, date_to, round=False)
            rate_cia = base_current.currency_id._convert(
                1, company_current.currency_id, cur, date_to, round=False)
            rate_act = company_current.currency_id._convert(
                1, cur.currency_id, cur, date_to, round=False)
            #_logger.info('Tasa:(%s) %s / %s = %s'%(date_to,company_current.currency_id.name, company_currency.name,rate))
            #_logger.info('Tasa:(%s) %s / %s = %s'%(date_to,base_current.currency_id.name, cur.currency_id.name, rate_cur))
            #_logger.info('Tasa:(%s) %s / %s = %s'%(date_to,base_current.currency_id.name, company_current.currency_id.name, rate_cia))
            #_logger.info('Tasa:(%s) %s / %s = %s'%(date_to,company_current.currency_id.name, cur.currency_id.name, rate_cia))
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
                # _logger.info('REQUEST:%s'%(request%params))
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
                #_logger.info('REQUEST INITIAL:%s'%(request%params))
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

    def _compute_subgroup_balance(self, accounts, rep_sing):
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
        grupo_obj = self.env['account.group']
        subgrupo_obj = self.env['account.subgroup']
        id_vacio = 999999

        sVacio = "GD%s-S%s" % (int(0), int(0))

        a_ids = []
        for x in accounts:
            a_ids.append(x)
        accxgrp = account_obj.search([('id', 'in', a_ids)], order='group_id')
        vagrp = {}

        for agrp in accxgrp:
            vagrp[agrp.group_id.id] = 0.0
        for agrp in accxgrp:
            vagrp[agrp.group_id.id] += accounts[agrp.id]['balance']

        if rep_sing:
            ragrp = sorted(vagrp.items(), key=lambda kv: (
                kv[1], kv[0]), reverse=False)
        else:
            ragrp = sorted(vagrp.items(), key=lambda kv: (
                kv[1], kv[0]), reverse=True)

        for grupo, balance in ragrp:
            sGrupo = '%04d' % (int(grupo) or 0)
            gdClave = "G%s" % sGrupo
            gtClave = "G%sT" % sGrupo
            accxsubgrp = account_obj.search(
                [('id', 'in', a_ids), ('group_id', '=', grupo)], order='subgroup_id')
            grp_id = grupo_obj.browse(grupo)
            if accxsubgrp:
                sagrp = {}
                tiene_subgrupo = False
                for agrp in accxsubgrp:
                    sagrp[agrp.subgroup_id.id] = 0.0
                    if agrp.subgroup_id:
                        tiene_subgrupo = True
                for agrp in accxsubgrp:
                    sagrp[agrp.subgroup_id.id] += accounts[agrp.id]['balance']
                stext = ""
                if rep_sing:
                    rsagrp = sorted(sagrp.items(), key=lambda kv: (
                        kv[1], kv[0]), reverse=False)
                else:
                    rsagrp = sorted(sagrp.items(), key=lambda kv: (
                        kv[1], kv[0]), reverse=True)
                if tiene_subgrupo:
                    res[gdClave] = dict.fromkeys(mapping, 0.0)
                    res[gdClave]['name'] = grp_id.name
                    res[gdClave]['type'] = 'tag'
                    res[gdClave]['level'] = 1
                    res[gdClave]['account_type'] = False
                    res[gdClave]['budget'] = 0.00
                    for subgrupo, sbalance in rsagrp:
                        subgrp_id = subgrupo_obj.browse(subgrupo)
                        if subgrp_id:
                            sSubgrupo = '%04d' % (int(subgrupo) or 0)
                            sClave = "G%s-S%s" % (sGrupo, sSubgrupo)
                            sg_name = "        "+subgrp_id.name
                            res[sClave] = dict.fromkeys(mapping, 0.0)
                            res[sClave]['name'] = sg_name
                            res[sClave]['type'] = 'detail'
                            res[sClave]['level'] = 1
                            res[sClave]['account_type'] = False
                            res[sClave]['budget'] = 0.00
                            res[sClave]['balance'] = sbalance
                    res[gtClave] = dict.fromkeys(mapping, 0.0)
                    res[gtClave]['name'] = "SUB-TOTAL "+grp_id.name
                    res[gtClave]['type'] = 'tittle'
                    res[gtClave]['level'] = 1
                    res[gtClave]['account_type'] = False
                    res[gtClave]['budget'] = 0.00
                    res[gtClave]['balance'] = balance
                else:
                    res[gdClave] = dict.fromkeys(mapping, 0.0)
                    res[gdClave]['name'] = grp_id.name
                    res[gdClave]['type'] = 'detail'
                    res[gdClave]['level'] = 1
                    res[gdClave]['account_type'] = False
                    res[gdClave]['budget'] = 0.00
                    res[gdClave]['balance'] = balance
            else:
                res[gdClave] = dict.fromkeys(mapping, 0.0)
                res[gdClave]['name'] = grp_id.name
                res[gdClave]['type'] = 'detail'
                res[gdClave]['level'] = 1
                res[gdClave]['account_type'] = False
                res[gdClave]['budget'] = 0.00
                res[gdClave]['balance'] = balance

        """
        for account in accounts:            
            account_id = account_obj.search([('id','=',account)])
            sg_id = account_id.subgroup_id and account_id.subgroup_id.id or id_vacio
            if sg_id==id_vacio:
                sg_name = _('It has no associated subgroup')
            else:
                sg_name = account_id.subgroup_id.name
            
            sGrupo = '%04d' % (int(account_id.group_id.id) or 0)
            sSubgrupo = '%04d' % (int(account_id.subgroup_id.id) or 0)  
            sClave = "G%s-S%s"%(sGrupo,sSubgrupo)
            gdClave = "G%s"%sGrupo
            gtClave = "G%sT"%sGrupo
                            
            if account_id.subgroup_id:
                if account_id.group_id:
                    sg_name = "        "+account_id.subgroup_id.name
                else:
                    sg_name = account_id.subgroup_id.name
                res[sClave] = dict.fromkeys(mapping, 0.0)
                res[sClave]['name'] = sg_name
                res[sClave]['type'] = 'detail'
                res[sClave]['level'] = 1
                res[sClave]['account_type'] = False
                res[sClave]['budget'] = 0.00
            elif account_id.group_id:
                res[gdClave] = dict.fromkeys(mapping, 0.0)
                res[gdClave]['name'] = account_id.group_id.name
                res[gdClave]['type'] = 'detail'
                res[gdClave]['level'] = 1
                res[gdClave]['account_type'] = False
                res[gdClave]['budget'] = 0.00
            else:
                res[sVacio] = dict.fromkeys(mapping, 0.0)
                res[sVacio]['name'] = account_id.group_id.name
                res[sVacio]['type'] = 'detail'
                res[sVacio]['level'] = 1
                res[sVacio]['account_type'] = False
                res[sVacio]['budget'] = 0.00
            if account_id.subgroup_id and account_id.group_id:
                res[gdClave] = dict.fromkeys(mapping, 0.0)
                res[gdClave]['name'] = account_id.group_id.name
                res[gdClave]['type'] = 'tag'
                res[gdClave]['level'] = 1
                res[gdClave]['account_type'] = False
                res[gdClave]['budget'] = 0.00
                                
                res[gtClave] = dict.fromkeys(mapping, 0.0)
                res[gtClave]['name'] = "SUB-TOTAL "+account_id.group_id.name 
                res[gtClave]['type'] = 'tittle'
                res[gtClave]['level'] = 1
                res[gtClave]['account_type'] = False
                res[gtClave]['budget'] = 0.00              
                                    
        for account in accounts:
            account_id = account_obj.search([('id','=',account)])
            sg_id = account_id.subgroup_id and account_id.subgroup_id.id or id_vacio
            
            sGrupo = '%04d' % (int(account_id.group_id.id) or 0)
            sSubgrupo = '%04d' % (int(account_id.subgroup_id.id) or 0)  
            sClave = "G%s-S%s"%(sGrupo,sSubgrupo)
            gdClave = "G%s"%sGrupo
            gtClave = "G%sT"%sGrupo
            
            for field in fields:
                #res[sg_id][field] += accounts[account][field]
                if account_id.subgroup_id:
                    res[sClave][field] += accounts[account][field]
                elif account_id.group_id:
                    res[gdClave][field] += accounts[account][field]
                else:
                    res[sVacio][field] += accounts[account][field]         
                if account_id.subgroup_id and account_id.group_id:                
                    res[gtClave][field] += accounts[account][field]
                    """
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
                    res[report.id]['account'], report.reverse_order)
            elif report.formula:
                safe_eval(report.formula, localdict, mode='exec', nocopy=True)
                res[report.id]['balance'] = float(localdict['result'])
            if report.sign and report.sign in ['+', '-']:
                rep_sing = 1.00
                if report.sign in ['-']:
                    rep_sing = -1.00
                res[report.id]['balance'] = abs(
                    res[report.id]['balance']) * rep_sing
                # for subgroup in res[report.id]['subgroup']:
                #    res[report.id]['subgroup'][subgroup]['balance'] = abs(res[report.id]['subgroup'][subgroup]['balance']) #* rep_sing
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
        _logger.info('used_context:%s' % (data.get('used_context')))
        _logger.info('year_prior_context:%s' %
                     (data.get('year_prior_context')))
        _logger.info('month_prior_context:%s' %
                     (data.get('month_prior_context')))
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
                subg_rec = []
                for k in [1]:
                    if k == 1:
                        subg = subgroup_bal.copy()
                    if k == 2:
                        subg = year_prior_subgroup.copy()
                    if k == 3:
                        subg = month_prior_subgroup.copy()
                    for j in subg:
                        if not(j in subg_rec):
                            subg_rec.append(j)  # ['name'] = subg[j]['name']
                subgroup_obj = self.env['account.subgroup'].search([])
                sg_max = len(subgroup_obj)
                sg_actual = 0
                subg_rec2 = sorted(subg_rec, key=lambda k: k,)
                for subg_id in subg_rec:
                    sg_actual += 1
                    if not ((subg_id in subgroup_bal) or (subg_id in year_prior_subgroup) or (subg_id in month_prior_subgroup)):
                        sg_actual = sg_max
                    cursor = {1}
                    if sg_actual == sg_max:
                        cursor = {2}
                    else:
                        cursor = {1}
                    for x in cursor:
                        if x == 1:
                            # record.name
                            sg_name = subgroup_bal[subg_id]['name']
                            sg_id = subg_id  # record.id
                            sg_sing = ' '  # report.sign
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
                                'type': subgroup_bal[subg_id]['type'],
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
                                'percent_diff_month': 0.00,
                                'code': subg_id
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

                            lines.append(vals)
            #_logger.info('lines: %s'%lines)
            #lines = sorted(lines, key = lambda kv:(kv[20], kv[2]))
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
        """
        if book.enable_consolidate:            
            companys = self.env['res.company'].browse([('parent_id','=',book.company_id.id)])
            if companys:
                result = ''
                for rec in companys:
                    if result:
                        result += '/ '
                    result += rec.name #self.env['res.company'].search([('id','=',rec)],limit=1).name
                    """
        return result

    def generate_xlsx_report(self, workbook, data, obj):
        context = self.env.context.copy()

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))

        init_balance = True
        sortby = None
        display_account = True

        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search(
                [('id', 'in', data['form']['journal_ids'])])]

        # if self.model == 'account.account' else self.env['account.account'].search([])
        accounts = docs

        if docs.enable_consolidate:
            selected_companies = self.env['res.company'].search(
                ['!', ('parent_id', '=', docs.company_id.id), ('id', '=', docs.company_id.id)])
            companies = []
            for x in selected_companies:
                companies.append(x.id)
            _logger.info('MULTI_COMPANY:%s' % companies)
        else:
            companies = [docs.company_id.id]
        # company_current = self.env['res.company']._company_default_get(
        #     'account')
        company_current = self.env.company
        moneda = company_current.currency_id.name
        report_res = self.get_account_lines(data.get('form'))

        report_name = accounts.account_report_id.name  # "Layout Profit and Loss"
        if data['form'].get('tag_id', False):
            report_name = "%s (sub-groups)" % report_name
        if data['form'].get('enable_consolidate', False):
            report_name = "%s - CONSOLIDATE" % report_name
        current_date = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        current_date = str(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p"))

        logged_users = self.env['res.users'].browse(1)
        logged_company = self.env['res.partner'].browse(1)
        company = data['form'].get('company_id', False)
        if company:
            logged_company = self.env['res.company'].browse(
                company[0]).partner_id

        solid_color = '#eaffff'
        solid_color = '#b7dee8'
        sheet = workbook.add_worksheet(report_name)
        format1 = workbook.add_format({'font_size': 22, 'bg_color': '#D3D3D3'})
        format4 = workbook.add_format({'font_size': 22})
        format2 = workbook.add_format(
            {'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3'})
        format22 = workbook.add_format({'font_size': 14})
        format23 = workbook.add_format({'font_size': 14, 'bold': True})
        format3 = workbook.add_format({'font_size': 10})
        format5 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF'})
        format7 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF'})
        format6 = workbook.add_format({'font_size': 22, 'bg_color': '#FFFFFF'})
        format66 = workbook.add_format(
            {'font_size': 22, 'bg_color': '#FFFFFF'})
        format22c = workbook.add_format({'font_size': 14})
        format22cb = workbook.add_format(
            {'font_size': 14, 'bg_color': solid_color})
        format22box_top = workbook.add_format(
            {'font_size': 14, 'bg_color': solid_color})
        format22box_mid = workbook.add_format(
            {'font_size': 14, 'bg_color': solid_color})
        format22box_bot = workbook.add_format(
            {'font_size': 14, 'bg_color': solid_color})
        format7.set_align('center')
        format66.set_align('center')
        format22c.set_align('center')
        format22cb.set_align('center')
        format22box_top.set_align('center')
        format22box_mid.set_align('center')
        format22box_bot.set_align('center')

        sheet.merge_range('B1:C1', self.company_tittle(docs), format66)
        sheet.write('B2', current_date, format3)
        sheet.write('B3:B3', report_name, format6)
        if data['form']['date_from']:
            date_start = _('From: %s') % data['form']['date_from']
        else:
            date_start = _('From: ')
        if data['form']['date_to']:
            date_end = data['form']['date_to']
        else:
            date_end = ""
        sheet.write('B4', _('Period'), format23)
        sheet.write('C4', date_start, format23)
        sheet.write('D4', _('To:'), format23)
        sheet.write('F4', date_end, format23)

        sheet.merge_range(
            'C6:D6', (data['form']['col_text_1']), format22box_top)
        sheet.merge_range(
            'F6:G6', (data['form']['col_text_1']), format22box_top)
        sheet.merge_range(
            'I6:J6', (data['form']['col_text_2']), format22box_top)
        sheet.merge_range(
            'L6:M6', (data['form']['col_text_3']), format22box_top)
        sheet.merge_range('O6:P6', ("Afwijking"), format22box_top)
        sheet.merge_range('R6:S6', ("Afwijking Tov"), format22box_top)
        sheet.merge_range('U6:V6', ("Afwijking Tov"), format22box_top)

        sheet.merge_range('C7:D7', ("Realisatie"), format22box_bot)
        sheet.merge_range('F7:G7', ("Begroting"), format22box_bot)
        sheet.merge_range('I7:J7', ("Realisatie"), format22box_bot)
        sheet.merge_range('L7:N7', ("Realisatie"), format22box_bot)
        sheet.merge_range('O7:P7', ("Tov Begroting"), format22box_bot)
        sheet.merge_range('R7:S7', ("Realisatie Vorig Jaar"), format22box_bot)
        sheet.merge_range('U7:V7', ("Realisatie Vorig Maand"), format22box_bot)

        sheet.write('B6', (""), format22cb)
        sheet.write('B7', (""), format22cb)
        sheet.write('B8', ("Descriptions"), format22cb)
        sheet.set_column('A:A', 1)
        sheet.set_column('B:B', 50)
        sheet.write('C8', (moneda), format22cb)
        sheet.set_column('C:C', 25)
        sheet.write('D8', ("%"), format22cb)
        sheet.set_column('D:D', 8)
        sheet.set_column('E:E', 0)
        sheet.write('F8', (moneda), format22cb)
        sheet.set_column('F:F', 25)
        sheet.write('G8', ("%"), format22cb)
        sheet.set_column('G:G', 8)
        sheet.set_column('H:H', 0)
        sheet.write('I8', (moneda), format22cb)
        sheet.set_column('I:I', 25)
        sheet.write('J8', ("%"), format22cb)
        sheet.set_column('J:J', 8)
        sheet.set_column('K:K', 0)
        sheet.write('L8', (moneda), format22cb)
        sheet.set_column('L:L', 25)
        sheet.write('M8', ("%"), format22cb)
        sheet.set_column('M:M', 8)
        sheet.set_column('N:N', 0)
        sheet.write('O8', (moneda), format22cb)
        sheet.set_column('O:O', 25)
        sheet.write('P8', ("%"), format22cb)
        sheet.set_column('P:P', 8)
        sheet.set_column('Q:Q', 0)
        sheet.write('R8', (moneda), format22cb)
        sheet.set_column('R:R', 25)
        sheet.write('S8', ("%"), format22cb)
        sheet.set_column('S:S', 8)
        sheet.set_column('T:T', 0)
        sheet.write('U8', (moneda), format22cb)
        sheet.set_column('U:U', 25)
        sheet.write('V8', ("%"), format22cb)
        sheet.set_column('V:V', 8)

        row_initial = 8
        row_number = row_initial
        col_number = 1
        data_format1 = workbook.add_format(
            {'bg_color': '#eaf4ff', 'font_size': 10})
        data_format1b = workbook.add_format(
            {'bg_color': '#eaf4ff', 'font_size': 10, 'bold': True})
        data_format2 = workbook.add_format(
            {'bg_color': '#ffffff', 'font_size': 10})
        data_format2b = workbook.add_format(
            {'bg_color': '#ffffff', 'font_size': 10, 'bold': True})
        data_format1.set_bold(False)
        data_format2.set_bold(False)
        row_sum = 9
        if data['form'].get('tag_id', False):
            row_sum = 1
            for x in report_res:
                if x['type'] in ['detail', 'tag']:
                    row_sum += 1
                else:
                    row_sum += 2
            row_sum += row_number
        balance_dif = 0
        year_prior_bal_dif = 0
        month_prior_bal_dif = 0
        for values in report_res:
            if row_number % 2 == 0:
                sheet.set_row(row_number, cell_format=data_format1)
                format3 = workbook.add_format(
                    {'bg_color': '#eaf4ff', 'font_size': 10})
                money = workbook.add_format(
                    {'bg_color': '#eaf4ff', 'font_size': 10, 'num_format': '#,##0.00'})
                percent_fmt = workbook.add_format(
                    {'bg_color': '#eaf4ff', 'font_size': 10, 'num_format': '0.0'})
            else:
                sheet.set_row(row_number, cell_format=data_format2)
                format3 = workbook.add_format(
                    {'bg_color': '#ffffff', 'font_size': 10})
                money = workbook.add_format(
                    {'bg_color': '#ffffff', 'font_size': 10, 'num_format': '#,##0.00'})
                percent_fmt = workbook.add_format(
                    {'bg_color': '#ffffff', 'font_size': 10, 'num_format': '0.0'})
            if 'tittle' in values['type']:
                format3.set_bold(True)
                money.set_bold(True)
                percent_fmt.set_bold(True)
                balance_dif += values['balance']
                year_prior_bal_dif += values['year_prior_bal']
                month_prior_bal_dif += values['month_prior_bal']
            if values['type'] == 'tag':
                format3.set_font_size(12)
                format3.set_bold(True)
            sname = "%s" % (values['name'])
            sheet.write(row_number, col_number, sname, format3)
            if values['type'] == 'tag':
                for i in range(1, 21):
                    sheet.write(row_number, col_number+i, '', format3)
                row_number += 1
                continue
            sheet.write(row_number, col_number + 1, values['balance'], money)
            sheet.write(row_number, col_number + 2, '=(C%s/C$%s)' %
                        (str(row_number+1), str(row_sum)), percent_fmt)  # values['percent_balance']
            sheet.write(row_number, col_number + 4, values['budget'], money)
            sheet.write(row_number, col_number + 5, '=F%s/F$%s' %
                        (str(row_number+1), str(row_sum)), percent_fmt)  # values['percent_budget']
            sheet.write(row_number, col_number + 7,
                        values['year_prior_bal'], money)
            sheet.write(row_number, col_number + 8, '=I%s/I$%s' % (str(row_number+1),
                                                                   str(row_sum)), percent_fmt)  # values['percent_year_prior_bal']
            sheet.write(row_number, col_number + 10,
                        values['month_prior_bal'], money)
            sheet.write(row_number, col_number + 11, '=L%s/L$%s' % (str(row_number+1),
                                                                    str(row_sum)), percent_fmt)  # values['percent_month_prior_bal']
            sheet.write(row_number, col_number + 13,
                        values['diff_budget'], money)
            sheet.write(row_number, col_number + 14, '=O%s/F%s' % (str(row_number+1),
                                                                   str(row_number+1)), percent_fmt)  # values['percent_diff_budget']
            sheet.write(row_number, col_number + 16,
                        values['diff_year'], money)
            sheet.write(row_number, col_number + 17, '=R%s/I%s' % (str(row_number+1),
                                                                   str(row_number+1)), percent_fmt)  # values['percent_diff_year']
            sheet.write(row_number, col_number + 19,
                        values['diff_month'], money)
            sheet.write(row_number, col_number + 20, '=U%s/L%s' % (str(row_number+1),
                                                                   str(row_number+1)), percent_fmt)  # values['percent_diff_month']
            row_number += 1
            if 'tittle' in values['type']:
                if row_number % 2 == 0:
                    sheet.set_row(row_number, cell_format=data_format1)
                    format3 = workbook.add_format(
                        {'bg_color': '#eaf4ff', 'font_size': 10})
                    money = workbook.add_format(
                        {'bg_color': '#eaf4ff', 'font_size': 10, 'num_format': '#,##0.00'})
                    percent_fmt = workbook.add_format(
                        {'bg_color': '#eaf4ff', 'font_size': 10, 'num_format': '0.0'})
                else:
                    sheet.set_row(row_number, cell_format=data_format2)
                    format3 = workbook.add_format(
                        {'bg_color': '#ffffff', 'font_size': 10})
                    money = workbook.add_format(
                        {'bg_color': '#ffffff', 'font_size': 10, 'num_format': '#,##0.00'})
                    percent_fmt = workbook.add_format(
                        {'bg_color': '#ffffff', 'font_size': 10, 'num_format': '0.0'})
                for i in range(0, 21):
                    sheet.write(row_number, col_number+i, '', format3)
                row_number += 1

        format3 = workbook.add_format({'bg_color': '#ffffff', 'font_size': 10})
        money = workbook.add_format(
            {'bg_color': '#ffffff', 'font_size': 10, 'num_format': '#,##0.00'})
        #sheet.set_row(row_number, cell_format=format3,height=3)
        for i in range(0, 21):
            sheet.write(row_number, col_number+i, '', format3)

        if data['form'].get('tag_id', False):
            format3.set_bold(True)
            money.set_bold(True)
            percent_fmt.set_bold(True)
            sheet.write(row_number, col_number, 'TOTAL', format3)
            sheet.write(row_number, col_number + 1, '=SUM(C'+str(row_initial+2) +
                        ':C' + str(row_sum-1) + ')-'+str(balance_dif), money)
            sheet.write(row_number, col_number + 4, '=SUM(F' +
                        str(row_initial+2) + ':F' + str(row_sum-1) + ')', money)
            sheet.write(row_number, col_number + 7, '=SUM(I'+str(row_initial+2) +
                        ':I' + str(row_sum-1) + ')-'+str(year_prior_bal_dif), money)
            sheet.write(row_number, col_number + 10, '=SUM(L'+str(row_initial+2) +
                        ':L' + str(row_sum-1) + ')-'+str(month_prior_bal_dif), money)

        row_number += 1

        workbook.close()
