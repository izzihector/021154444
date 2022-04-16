from odoo import api , fields, models,_
from odoo.exceptions import AccessError, ValidationError


class HotelPeriod(models.Model):
    _name = 'hotel.period.lead'

    name = fields.Char()
    is_parent = fields.Selection([('Yes','Yes'),('No','No')],default="No")
    main_period = fields.Many2one('hotel.period.lead',domain="[('is_parent','=','Yes')]")
    date_from = fields.Date()
    date_to =fields.Date()
    lead_days = fields.Integer()
    note = fields.Text()

    @api.onchange('date_from','date_to','main_period')
    def check_unique(self):
        self.ensure_one()
        print("in PEriodsn")
        if self.date_from and self.date_to:
            print(self.date_from," date form",self.date_to,"=======================",'date to')
            period_lead_ids = self.env['hotel.period.lead'].search([])
            for period_lead_id in period_lead_ids:
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print(self.date_from,'self date from ', period_lead_id.date_from,'period date from')
                print(self.date_from, period_lead_id.date_to)
                if self.date_from >= period_lead_id.date_from and self.date_from <= period_lead_id.date_to:
                    print(self.main_period.id , period_lead_id.id,"----------------")
                    if not self.main_period.id == period_lead_id.id:
                        raise ValidationError(_(" Start From Date is conflict With another Period ."))
                elif self.date_to >= period_lead_id.date_from and self.date_to <= period_lead_id.date_to:
                    if not self.main_period.id == period_lead_id.id:
                        raise ValidationError(_(" End  Date is conflict With another Period ."))

    @api.onchange('is_parent')
    def clear_main_period(self):
        if self.is_parent =="Yes":
            self.main_period = False

