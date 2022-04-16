# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class GSDailySales(models.Model):
    _name = 'gs.daily.sales'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Daily Sales'
    _rec_name = "station_id"

    state = fields.Selection([
                        ('draft', 'Draft'),
                        ('submit', 'Submitted'),
                        ('approve', 'Approved')], readonly=True, default='draft', copy=False, string="Status")

    daily_sales_ids = fields.One2many('gs.daily.sales.line', 'link_id')
    station_id = fields.Many2one('gs.petrol.station', string='Station')
    date = fields.Date(string='Date', )
    move_id = fields.Many2one('account.move',)
    order_id = fields.Many2one('sale.order',)

    def action_submit(self):
        for rec in self:
            rec.state = 'submit'

    @api.onchange('station_id')
    def domain_station_id(self):
        return {'domain': {'station_id': [('id', 'in', self.env.user.station_ids.ids)]}}

    # def action_create_invoice(self):
    #     for x in self:
    #         lines = [(5, 0, 0)]
    #         invoice = 0
    #         move_vals_list = []
    #         for pump in x.daily_sales_ids:
    #             val = {
    #                 'product_id': pump.product_id.id,
    #                 'name': pump.product_id.name,
    #                 'account_id': 1,
    #
    #             }
    #             lines.append((0, 0, val))
    #             invoice = lines
    #         if invoice:
    #             move_vals_list.append({
    #                 'move_type': 'out_invoice',
    #                 'invoice_date': fields.Date.today(),
    #                 'currency_id': self.env.company.currency_id.id,
    #                 'invoice_line_ids': invoice
    #             })
    #             x.move_id = self.env['account.move'].create(move_vals_list)

    def action_create_quotations(self):
        for x in self:
            lines = [(5, 0, 0)]
            quotations = 0
            move_vals_list = []
            for pump in x.daily_sales_ids:
                tax = pump.product_id.taxes_id.ids
                val = {
                    'product_id': pump.product_id.id,
                    'name': pump.product_id.name,
                    'product_uom_qty': pump.sales,
                    'tax_id': tax,
                }
                lines.append((0, 0, val))
                quotations = lines
            if quotations:
                move_vals_list.append({
                    'partner_id': self.station_id.partner_id.id,
                    'warehouse_id': self.station_id.warehouse_id.id,
                    'workflow_process_id': self.env.ref('sale_automatic_workflow.automatic_validation').id,
                    'order_line': quotations,
                })
                x.order_id = self.env['sale.order'].create(move_vals_list)
                x.order_id.action_confirm()
                # x.order_id.picking_ids.button_validate()
                x.state = 'approve'


class GSDailySalesLine(models.Model):
    _name = 'gs.daily.sales.line'

    link_id = fields.Many2one('gs.daily.sales')
    date = fields.Date(string='Date', )
    type_pump_id = fields.Many2one('gs.pump.type', string='Pump Type')
    nozzle_petrol_id = fields.Many2one('gs.nozzle.petrol', string='Nozzle Petrol')
    product_id = fields.Many2one('product.product', string='Product', related='type_pump_id.product_id',)
    opening_pump = fields.Float(string='Opening',)
    ending_pump = fields.Float(string='Ending',)
    sales = fields.Float(string='Sales',)
    user_id = fields.Many2one('res.users', string='User')
