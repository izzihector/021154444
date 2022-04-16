# -*- coding: utf-8 -*-
from datetime import date
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"
    unlocked_periods = fields.One2many('account.move.unlocked.period', 'company_id', string='Unlocked periods')


class AccountMove(models.Model):
    _inherit = "account.move"

    
    def _check_lock_date(self):
        for move in self:
            lock_date = max(move.company_id.period_lock_date or date.min,
                            move.company_id.fiscalyear_lock_date or date.min)
            if self.user_has_groups('account.group_account_manager'):
                lock_date = move.company_id.fiscalyear_lock_date
            if move.date <= (lock_date or date.min) \
                    and not self._check_lock_date_exceptions(move.date, move.company_id):
                if self.user_has_groups('account.group_account_manager'):
                    message = _("You cannot add/modify entries prior to and inclusive of the lock date %s") % (
                        lock_date)
                else:
                    message = _(
                        "You cannot add/modify entries prior to and inclusive of the lock date %s. Check the company "
                        "settings or ask someone with the 'Adviser' role") % (
                                  lock_date)
                raise UserError(message)
        return True

    def _check_lock_date_exceptions(self, move_date, company):
        for period in company.unlocked_periods:
            if period.date_to >= move_date >= period.date_from:
                return True
        return False


class AccountMoveUnlockedPeriod(models.Model):
    _name = "account.move.unlocked.period"

    company_id = fields.Many2one('res.company', string="Company", ondelete="cascade", index=True,
                                 required=True, auto_join=True)
    date_from = fields.Date('Date from', required=True)
    date_to = fields.Date('To date', required=True)


AccountMove()
