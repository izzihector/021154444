from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PaymentInherit2(models.Model):
    _inherit = 'account.payment'

    @api.onchange('date')
    def _onchange_date_validation(self):
        if self.date:
            if self.date < fields.Date.today():
                raise ValidationError(_("You Cannot Enter Date Before Today"))
