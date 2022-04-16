# -*- encoding: UTF-8 -*-

from odoo import api, fields, models, _


class MandatoryAnalyticAccount(models.Model):
    _name = 'account.analytic.mandatory'

    account_id = fields.Many2one('account.account', 'Account')
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic accounts required')
    mandatory_vlnr = fields.Many2many('account.analytic.account', string='Flight number required',
                                      relation='account_analytic_account_account_analytic_mandatory_vlnr_rel')
    excluded_analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic accounts excluded',
                                                     relation='account_analytic_account_account_analytic_mandatory_exc_rel')

    @staticmethod
    def search_mandatory_accounts(code, cr):
        sql = """
            SELECT account_analytic_account_id
            FROM account_analytic_mandatory AAM
                   JOIN account_account AA ON (AA.id = AAM.account_id)
                   JOIN account_analytic_account_account_analytic_mandatory_rel AMV
                     on AAM.id = AMV.account_analytic_mandatory_id
            WHERE AA.code = %s 
        """

        cr.execute(sql, (code,))
        results = cr.dictfetchall()
        if results:
            return [result['account_analytic_account_id'] for result in results]
        else:
            sql = """
                SELECT id
                FROM account_analytic_account
                WHERE id NOT IN (SELECT AAAAMER.account_analytic_account_id
                                 FROM account_analytic_mandatory AAM
                                        JOIN account_account AA ON (AA.id = AAM.account_id)
                                        JOIN account_analytic_account_account_analytic_mandatory_exc_rel AAAAMER
                                          ON (AAM.id = AAAAMER.account_analytic_mandatory_id)
                                 WHERE AA.code = %s);
            """
            cr.execute(sql, (code,))
            results = cr.dictfetchall()
            if results:
                return [result['id'] for result in results]

    @staticmethod
    def check_required_fligh_number(code, account_analytic_id, cr):
        sql = """
            SELECT account_analytic_account_id
            FROM account_analytic_mandatory AAM
                   JOIN account_account AA ON (AA.id = AAM.account_id)
                   JOIN account_analytic_account_account_analytic_mandatory_vlnr_rel AMV
                     on AAM.id = AMV.account_analytic_mandatory_id
            WHERE AA.code = %s AND AMV.account_analytic_account_id = %s
        """
        cr.execute(sql, (code, account_analytic_id))
        return cr.dictfetchall()
