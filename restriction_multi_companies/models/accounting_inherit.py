# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class UomCategoryInherit(models.Model):
    _inherit = "uom.category"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


class UomUomInherit(models.Model):
    _inherit = "uom.uom"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)


class ProductCategoryInherit(models.Model):
    _inherit = "product.category"

    company_id = fields.Many2one('res.company', string='Company')
