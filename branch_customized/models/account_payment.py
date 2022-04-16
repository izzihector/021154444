from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        pos_session_id = vals.get('name')
        pos_session = []
        if pos_session_id:
            pos_session = self.env['pos.session'].search([('name', '=', pos_session_id)])
        if not 'branch_id' in vals and pos_session:
            vals.update({
                'branch_id': pos_session.config_id.branch_id.id
            })
        return super(AccountPayment, self).create(vals)
