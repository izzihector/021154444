from odoo import models, fields, api


class AccountChangeLockDate(models.TransientModel):
    """
    This wizard is used to change the lock date
    """
    _inherit = 'account.change.lock.date'
    _description = 'Change Lock Date'

    unlocked_periods = fields.One2many('account.change.unlocked.period', 'lock_dates', string='Unlocked periods',
                                       default=lambda self: [{'date_from': period.date_from, 'date_to': period.date_to}
                                                             for period in self.env.user.company_id.unlocked_periods], )

    
    def change_lock_date(self):
        self.env.user.company_id.unlocked_periods = False
        self.env.user.company_id.write(
            {
                'period_lock_date': self.period_lock_date,
                'fiscalyear_lock_date': self.fiscalyear_lock_date,
                'unlocked_periods': [(0, 0, {'date_from': period.date_from, 'date_to': period.date_to}) for period in
                                     self.unlocked_periods]
            }
        )
        return {'type': 'ir.actions.act_window_close'}


class AccountChangeUnlockedPeriod(models.TransientModel):
    _name = "account.change.unlocked.period"

    lock_dates = fields.Many2one('account.change.lock.date', string="Lock dates")
    date_from = fields.Date('From date')
    date_to = fields.Date('To date')
