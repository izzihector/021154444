from odoo import api,models,fields


class OpportunityReservation(models.Model):
    _inherit = 'crm.lead'

    order_from =fields.Char(string="Guest Name",required=True)
    reservation_id = fields.Many2one('hotel.reservation.management',readonly=True)

    def opportunity_reservation_form(self):
        self.ensure_one()
        view = self.env.ref('hotel_reservation_mangement.hotel_reservation_management_form')
        print(view,"10000000")
        ctx = dict()
        ctx.update({
            'default_order_from': self.partner_id.id,
            'default_guest_name': self.order_from,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_source_id': self.source_id.id,
            'default_opportunity_id': self.id,

        })
        return {
            # 'domain': "[('id','=', " + str(resr_id.id) + ")]",
            'view_type': 'form',
            'view_mode': 'form',
            'view_id':view.id,
            'res_model': 'hotel.reservation.management',
            'target':'current',
            'type': 'ir.actions.act_window',
            'context':ctx,

        }
