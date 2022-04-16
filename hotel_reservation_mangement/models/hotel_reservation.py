from odoo import fields, api, models, _
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, UserError
from odoo.exceptions import AccessError, ValidationError


class HotelReservation(models.Model):
    _name = 'hotel.reservation.management'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    reservation_state = [
        ('Draft', 'Draft'),
        ('Confirmed', 'Confirmed'),
        ('To Invoice', 'To Invoice'),
        ('Invoiced', 'Invoiced'),
        ('Canceled', 'Canceled'),
    ]

    name = fields.Char(string='Reservation #', readonly=True, size=64, default=lambda *a: '#')

    hotel_id = fields.Many2one('hotel.management', required=True)
    room_type = fields.Many2one('hotel.room.type', required=True, domain="[('hotel_id','=',hotel_id)]")
    meal_plan = fields.Selection([
        ('Soft Al Inclusive', 'Soft Al Inclusive'),
        ('Half Board (HB)', 'Half Board (HB)'),
        ('Full Board (FB)', 'Full Board (FB)'),

    ], required=True, tracking=True)
    arrival_date = fields.Date(string="Check in", required=True)
    nights_quantity = fields.Integer(string="Nights ", default=1)
    departure_date = fields.Date(track_visibility='onchange', string="Check Out")

    adults = fields.Integer()
    children = fields.Integer()
    total = fields.Integer(string="Total Pax")
    guest_name = fields.Char()
    order_from = fields.Many2one('res.partner', string='Order By')
    room_quantity = fields.Integer(track_visibility='onchange', required=True)
    reserved_room_quantity = fields.Integer(compute='get_total_price_and_reserved_rooms', store=True,
                                            string="Room Counter", readonly=True)
    note = fields.Text()
    state = fields.Selection(reservation_state, default='Draft')
    total_price = fields.Integer(compute='get_total_price_and_reserved_rooms', store=True, )
    split_room_ids = fields.One2many('split.room', 'reservation_id')
    children_room_ids = fields.One2many('children.split.room', 'reservation_id')
    reservation_date = fields.Date(readonly=True, default=fields.Date.today)
    # track_visibility = 'onchange',
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, default=lambda self: self.env.user)

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    account_id = fields.Many2one('account.account', string='Account', required=True,
                                 domain=[('deprecated', '=', False)])
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic account')

    opportunity_id = fields.Many2one('crm.lead', readonly=True)
    campaign_id = fields.Many2one('utm.campaign', 'Campaign',
                                  required=True, ondelete='cascade',
                                  help="This name helps you tracking your different campaign efforts, e.g. Fall_Drive, Christmas_Special")
    source_id = fields.Many2one('utm.source', string='Source',
                                help="This is the link source, e.g. Search Engine, another domain,or name of email list",
                                default=lambda self: self.env.ref('utm.utm_source_newsletter', False))
    medium_id = fields.Many2one('utm.medium', string='Medium',
                                help="This is the delivery method, e.g. Postcard, Email, or Banner Ad",
                                default=lambda self: self.env.ref('utm.utm_medium_email', False))

    invoice_count = fields.Integer(compute='_invoice_count', string="Invoice")
    invoice_id = fields.Many2one('account.move', readonly=True)
    room_nights = fields.Integer("Room Nights", compute='get_total_price_and_reserved_rooms', store=True, )

    # @api.multi
    def _invoice_count(self):
        res_invoice = self.env['account.move']
        for inv in self:
            if inv.id:
                invoice_ids = self.env['account.move'].search([('reservation_id', '=', inv.id)])
                invoices = res_invoice.browse(invoice_ids)
                invoice_count = 0
                for inv_id in invoices:
                    invoice_count += 1
                inv.invoice_count = invoice_count
        return True

    # @api.multi
    def check_invoice_state(self):
        invoice_obj = self.env['account.move'].search([('reservation_id', '=', self.id)])
        massage = ''
        if invoice_obj.state == 'draft':
            massage = "This Invoice has no Payments Due Amount  " + str(invoice_obj.amount_total)
        elif invoice_obj.state == 'open':
            massage = "This Invoice isn't Fully Invoiced Residual Amount : " + str(invoice_obj.residual)
        elif invoice_obj.state == 'paid':
            massage = "This Invoice is Fully Invoiced Residual Amount : " + str(invoice_obj.residual)
            self.state = "Invoiced"
            self.mark_as_won()
        return self.invoice_massage(massage)

    def invoice_massage(self, massage):
        view = self.env.ref('hotel_reservation_mangement.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = massage
        return {
            'name': "Invoice Checked",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    def mark_as_won(self):
        stage_obj = self.env['crm.stage'].search([('name', '=', 'Won')])
        print(stage_obj)
        if self.opportunity_id.id:
            opp_obj = self.env['crm.lead'].search([('id', '=', self.opportunity_id.id)])
            print(opp_obj)
            opp_obj.stage_id = stage_obj.id

    @api.onchange('adults', 'children')
    def cal_total(self):
        self.total = self.adults + self.children

    @api.onchange('hotel_id')
    def set_hotel_room(self):
        if self.room_type:
            self.room_type = False

    # odoo 11

    # @api.onchange('nights_quantity')
    # def set_departure_date(self):
    #     print("i am in night onchange")
    #     if self.arrival_date:
    #         arrival_date = datetime.strptime(self.arrival_date, DATE_FORMAT)
    #         departure_date = arrival_date + timedelta(days=self.nights_quantity)
    #         departure_date_str = fields.Datetime.to_string(departure_date)
    #         print(departure_date)
    #         self.departure_date = departure_date_str

    # odoo 12
    @api.onchange('nights_quantity')
    def set_departure_date(self):
        print("i am in night onchange", self.arrival_date)
        if self.arrival_date:
            arrival_date = self.arrival_date
            departure_date = arrival_date + timedelta(days=self.nights_quantity)
            self.departure_date = departure_date

    # odoo 11
    # @api.onchange('departure_date')
    # def set_nights_quantity_date(self):
    #     if self.arrival_date:
    #         arrival_date = datetime.strptime(self.arrival_date, DATE_FORMAT)
    #         departure_date = datetime.strptime(self.departure_date, DATE_FORMAT)
    #         print(departure_date)
    #         print(departure_date - arrival_date)
    #         self.nights_quantity = (departure_date - arrival_date).days

    # odoo 12
    # @api.onchange('departure_date')
    def set_nights_quantity_date(self):
        if self.arrival_date and self.departure_date:
            arrival_date = self.arrival_date
            departure_date = self.departure_date
            print(departure_date)
            print(departure_date - arrival_date)
            self.nights_quantity = (departure_date - arrival_date).days

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('hotel.reservation.management')
        vals['name'] = sequence
        reservation = super(HotelReservation, self).create(vals)
        if self.opportunity_id:
            crm_lead_obj = self.env['crm.lead'].search([('id', '=', vals['opportunity_id'])], limit=1)
            print(crm_lead_obj, "DDDDaaddfcsdf")
            crm_lead_obj.reservation_id = reservation.id
            print(reservation.id, reservation.name, "readsfdadgvsfgfsd")
        return reservation

    # @api.multi
    def unlink(self):
        if self.state != 'Draft':
            raise UserError(_("You cannot delete an reservation order if the state is not 'Draft'."))
        return super(HotelReservation, self).unlink()

    # @api.multi
    def confirm_reservation(self):
        if self.reserved_room_quantity == self.room_quantity:
            for line in self.split_room_ids:
                line.reservation_calendar()
            self.state = 'Confirmed'
        else:
            raise ValidationError(_("You Must Reserve Rooms First"))

    # @api.multi
    def reservation_calendar(self):
        room_cal_obj = self.env['hotel.room.capacity']
        for reservation_nights in range(0, self.nights_quantity):
            day_date = self.arrival_date + timedelta(days=reservation_nights)
            print(day_date)
            room_cal_id = room_cal_obj.search(
                [('hotel_id', '=', self.hotel_id.id), ('room_type_id', '=', self.room_type.id),
                 ('date_day', '=', day_date)])
            print(room_cal_id, "==========================")
            if room_cal_id:
                reserved_room = self.room_quantity + room_cal_id.reserved_room
                if reserved_room > room_cal_id.total_rooms:
                    raise ValidationError(_("You are Exceed Reservations Rooms For that day " + fields.Date.to_string(
                        room_cal_id.date_day)))
                room_cal_id.reserved_room = reserved_room
            else:
                room_cal_obj.create(
                    {'date_day': day_date, 'room_type_id': self.room_type.id, 'hotel_id': self.hotel_id.id,
                     'reserved_room': self.room_quantity})
        return True

    @api.onchange('room_type', 'meal_plan', 'arrival_date', 'departure_date')
    def at_any_changes_in_form(self):
        self.set_nights_quantity_date()
        if self.split_room_ids:
            for line in self.split_room_ids:
                print("update reservation lines")
                line.update({'hotel_id': self.hotel_id.id, 'room_type': self.room_type.id, 'meal_plan': self.meal_plan,
                             'arrival_date': self.arrival_date, 'departure_date': self.departure_date
                             })
                line.calc_room_price_for_total_guests()

    # @api.multi
    def cancel_reservation(self):
        if self.state != "Draft":
            for line in self.split_room_ids:
                line.cancel_reservation_calendar()
        self.state = 'Canceled'

    # @api.multi
    def draft_reservation(self):
        if self.state != "Draft":
            for line in self.split_room_ids:
                line.cancel_reservation_calendar()
        self.state = 'Draft'

    @api.depends('split_room_ids')
    def get_total_price_and_reserved_rooms(self):
        for rec in self:
            total_price = 0
            reserved_rooms = 0
            total_adults = 0
            room_nights = 0
            for split_room_id in rec.split_room_ids:
                total_price += split_room_id.nights_price
                reserved_rooms += split_room_id.room_quantity
                total_adults += int(split_room_id.person_per_room)
                room_nights += split_room_id.nights_quantity
                if reserved_rooms > rec.room_quantity:
                    raise ValidationError(_('You Reserve more than total rooms you want .'))
            rec.update(
                {'total_price': total_price, 'room_nights': room_nights, 'reserved_room_quantity': reserved_rooms,
                 'adults': total_adults})

    # @api.multi
    def write(self, vals):
        if vals.get('split_room_ids'):
            total_price = 0
            reserved_rooms = 0
            for split_room_id in self.split_room_ids:
                total_price += split_room_id.nights_price
                reserved_rooms += split_room_id.room_quantity
                if reserved_rooms > self.room_quantity:
                    raise ValidationError(_('You Reserve more than total rooms you want .'))
                print(total_price, reserved_rooms, "=================")
                vals['total_price'] = total_price
                vals['reserved_room_quantity'] = reserved_rooms
        return super(HotelReservation, self).write(vals)

    # @api.one
    @api.constrains('arrival_date', 'departure_date')
    def _check_date(self):
        print(" Prevents the user to create an order in the past")
        date_in = self.arrival_date
        date_out = self.departure_date
        date_today = self.reservation_date
        if date_in < date_today or date_out < date_today:
            raise ValidationError(_('The date of your order is in the past .'))
        if date_out <= date_in:
            raise ValidationError(_('The date of your  check out must br after check in .'))

    # @api.one
    @api.constrains('reserved_room_quantity')
    def _check_rooms(self):
        print(" reservations rooms qunatity")
        total_rooms = self.room_quantity
        reserved_quantity = self.reserved_room_quantity
        if total_rooms < reserved_quantity:
            raise ValidationError(_('You Reserve more than total rooms you want .'))

    # @api.multi
    def update_invoice(self):
        for reservation in self:
            reservation.check_invoice_state()
            invoice_obj = self.env["account.move"].search([('reservation_id', '=', reservation.id)])
            print(invoice_obj.name, invoice_obj.origin)
            invoice_line_obj = self.env["account.move.line"]
            if invoice_obj.state == 'draft':
                invoice_obj.invoice_line_ids = [(5, 0, 0)]
                prd_account_id = self.account_id.id
                print(prd_account_id, "=============================")
                # Create Invoice line
                for room_list_id in reservation.split_room_ids:
                    check_in_date = fields.Date.to_string(room_list_id.arrival_date)
                    check_out_date = fields.Date.to_string(room_list_id.departure_date)
                    curr_invoice_line = {
                        'name': "Guest name ( " + room_list_id.name + ')  - Check In (' + check_in_date +
                                ') , Check Out ( ' + check_out_date + ') , Adults ('
                                + room_list_id.person_per_room + " ) Children ( " + str(room_list_id.children) + ') .',
                        'price_unit': room_list_id.nights_price,
                        'quantity': 1,
                        'account_id': prd_account_id,
                        'account_analytic_id': self.account_analytic_id.id,
                        'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                        'invoice_id': invoice_obj.id,
                    }
                    inv_line_ids = invoice_line_obj.create(curr_invoice_line)
                    invoice_obj.invoice_line_ids = [(4, 0, inv_line_ids.ids)],

    def invoice_reservation(self):
        invoice_obj = self.env["account.move"]
        invoice_line_obj = self.env["account.move.line"]
        inv_ids = []
        for reservation in self:
            # Create Invoice
            if reservation.order_from:
                curr_invoice = {
                    'partner_id': reservation.order_from.id,
                    'account_id': reservation.order_from.property_account_receivable_id.id,
                    'reservation_id': reservation.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    'date_invoice': fields.Date.today(),
                    'origin': reservation.name,
                    'hotel_id': reservation.hotel_id.id,
                    'room_type': reservation.room_type.id,
                    'meal_plan': reservation.meal_plan,
                    'arrival_date': reservation.arrival_date,
                    'departure_date': reservation.departure_date,
                    'nights_quantity': reservation.nights_quantity,
                }

                inv_ids = invoice_obj.create(curr_invoice)
                inv_id = inv_ids.id

                if inv_ids:
                    prd_account_id = self.account_id.id
                    print(prd_account_id, "++++++++++++++++=============")
                    # Create Invoice line
                    for room_list_id in reservation.split_room_ids:
                        check_in_date = fields.Date.to_string(room_list_id.arrival_date)
                        check_out_date = fields.Date.to_string(room_list_id.departure_date)
                        curr_invoice_line = {
                            'name': "Guest name ( " + room_list_id.name + ')  - Check In (' + check_in_date +
                                    ') , Check Out ( ' + check_out_date + ') , Adults ('
                                    + room_list_id.person_per_room + " ) Children ( " + str(
                                room_list_id.children) + ') .',
                            'price_unit': room_list_id.nights_price,
                            'quantity': 1,
                            'account_id': prd_account_id,
                            'account_analytic_id': self.account_analytic_id.id,
                            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                            'invoice_id': inv_id,
                        }
                        reservation.update({'invoice_id': inv_id})
                        inv_line_ids = invoice_line_obj.create(curr_invoice_line)

                self.write({'state': 'To Invoice'})
            return True
