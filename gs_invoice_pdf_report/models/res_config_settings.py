from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    print_qr = fields.Boolean(default=True)

class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    print_qr = fields.Boolean('Print QR Code', related="company_id.print_qr", readonly=False,
                              help="""If ticked, you can print the invoice URL as QR Code in account invoice""",
                              config_parameter='gs_invoice_qr.print_qr', default=True)