from odoo import api, fields, models


class HotelManagement(models.Model):
    _name = 'hotel.management'
    _inherit = ['mail.thread']
    _inherits = {
        'res.partner': 'partner_id',
    }
    _description = "it's service Description"

    rates = [('1 stare ', '1 stare *'),
             ('2 stare', '2 stare ** '),
             ('3 stare', '3 stare ***'),
             ('4 stare', '4 stare ****'),
             ('5 stare', '5 stare *****'),
             ('class A', 'class A'),
             ('class B', 'class B'),
             ('class C', 'class C'),
             ('1st class', '1st class'),
             ('2st class', '2st class'),
             ('3st class', '3st class'),
             ]

    official_rate = fields.Selection(rates)
    type_of_hotel = fields.Char("Hotel Type")
    type = fields.Selection([('individual', 'Independent'), ('company', 'Chain')], default='individual')
    location_url = fields.Char("Google Map Url")
    hotel_parent = fields.Many2one('res.company', string='Main Chain')
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 help='Partner-related data of the Hotel')
    total_rooms = fields.Integer(required=True, )
    note = fields.Text()
    time_available = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="IS 24 Hours Available")
    check_in_time = fields.Float()
    check_out_time = fields.Float()

    @api.model
    def create(self, vals):
        # vals['supplier'] = True
        # vals['is_hotel'] = True
        health_patient = super(HotelManagement, self).create(vals)
        return health_patient
