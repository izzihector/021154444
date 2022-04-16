from odoo.exceptions import Warning
from odoo import api, fields, models


class promotional_schemes(models.Model):
    _name = 'loyalty.promotional.schemes'
    _description = 'Promotional Scheme'

    name = fields.Char('Scheme Name', size=64, required=True)
    state = fields.Selection([
        ('draft', 'Request'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    ], 'Status', readonly=True, default='draft', index=True)
    scheme_type = fields.Selection([
        ('buy_x_get_y', 'Buy X Get Y Free'),
        ('unit_price_disc_amt', 'Unit Price Disc. (Amt.)'),
        ('unit_price_disc_percent', 'Unit Price Disc. (%)'),
        ('volume_discount', 'Volume Discount'),
    ], 'Scheme Type', default='buy_x_get_y')
    scheme_basis = fields.Selection([
        ('on_same_prod', 'On Same Product'),
        ('on_diff_prod', 'On Different Product'),
    ], 'Scheme Basis', default='on_same_prod')
    scheme_id = fields.Many2one('stock.warehouse', 'Scheme ID')
    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    available_on = fields.One2many('loyalty.available_on', 'scheme_id', 'Available On')
    scheme_product = fields.One2many('loyalty.available_on', 'scheme_id2', 'Scheme Product')
    buy_a_qty = fields.Integer('Buy A Qty in Full Price', required=True)
    get_a_qty = fields.Integer('Get A Qty in Discount', required=True)
    discount = fields.Integer('Discount in %', required=True)
    qty_disc = fields.One2many('loyalty.qty.disc', 'buyx_gety_id', 'Select Qty and Disc.')
    buy_a_qty_in_volume = fields.Integer('Buy A Qty', required=True)
    offer_price = fields.Float('Offer Price', required=True)

    def approve(self):
        self.write({'state': 'approve'})

    def cancel(self):
        self.write({'state': 'cancel'})


class qty_disc(models.Model):
    _name = 'loyalty.qty.disc'
    _description = 'Select Quantity and Discount'

    buyx_gety_id = fields.Many2one('loyalty.promotional.schemes', 'loyalty_promotional_scheme_ref')
    qty = fields.Float('Quantity')
    discount = fields.Float('Discount')


class available_on_template(models.Model):
    _name = 'loyalty.available_on'
    _description = "Loyalty available on product template"

    name = fields.Char('Name', size=64)
    scheme_id = fields.Many2one('loyalty.promotional.schemes', 'Scheme Ref.')
    scheme_id2 = fields.Many2one('loyalty.promotional.schemes', 'Scheme Ref1.')
    template_id = fields.Many2one('product.template', 'Template', required=True)
    product_list = fields.Many2many('product.product', 'loyalty_product_rel', 'loyalty_id', 'product_id', string='Select Products')

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            products_ids = self.env['product.product'].search([('product_tmpl_id', '=', self.template_id.id)])
            self.product_list = products_ids
