# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    contact_name = fields.Char('Contact Name')
    cr_id = fields.Char('CR ID')
