from odoo import fields, models, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'
    _description = 'Arabic Address Description'

    street1 = fields.Char()
    street21 = fields.Char()
    zip1 = fields.Char()
    city1 = fields.Char()
    country_id1 = fields.Char(string="Country")
    name1 = fields.Char(string='Company Arabic Name', required=False)
    bank_account_ids = fields.One2many('account.journal','company_id',string='Bank Accounts')
    whatsapp_no = fields.Char(string='Whatsapp NO')