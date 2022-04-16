from odoo import fields, api, models, _
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.exceptions import AccessError, ValidationError


class CreditNoteReservation(models.Model):
    _name = 'reservation.credit.note'
    _inherit ='hotel.reservation.management'

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('Reservation.credit.note')
        vals['name'] = sequence
        reservation = super(CreditNoteReservation, self).create(vals)
        if self.opportunity_id:
            crm_lead_obj = self.env['crm.lead'].search([('id', '=', vals['opportunity_id'])], limit=1)
            print(crm_lead_obj, "DDDDaaddfcsdf")
            crm_lead_obj.reservation_id = reservation.id
            print(reservation.id, reservation.name, "readsfdadgvsfgfsd")
        return reservation