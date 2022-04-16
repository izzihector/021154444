from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    api_origin = fields.Char('API Origin')
    enroll_no = fields.Char('Enroll No')
    name_bangla = fields.Char('Bangla Name')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('common', 'Common')])
    warehouse_id = fields.Many2one('stock.warehouse', string='Outlet', store=True)
    partner_type = fields.Selection([('b2b', 'B2B'), ('b2c', 'B2C'), ('other', 'Walk-in-Customer')], default='b2b')
    image_id = fields.Char("ERP Image ID")
    company_id = fields.Many2one('res.company')
