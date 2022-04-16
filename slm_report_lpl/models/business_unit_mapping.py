# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BusinessUnitMapping(models.Model):
    _name = 'business.unit.mapping'

    name = fields.Char('Name')
    line_ids = fields.One2many('business.unit.mapping.line', 'business_unit_mapping_id',
                               string='Business Unit Mapping lines', copy=True)
    layout_lines = fields.One2many('business.unit.report.layout', 'business_unit_mapping_id',
                                   string='Business Unit Layout Lines', copy=True)
    profit_center = fields.Many2one('account.analytic.account', 'Profit Center account')


class BusinessUnitMappingLine(models.Model):
    _name = 'business.unit.mapping.line'

    business_unit_mapping_id = fields.Many2one('business.unit.mapping', string='Business Unit Mapping',
                                               ondelete="cascade",
                                               index=True, required=True, auto_join=True)
    is_account_tag = fields.Boolean('Is account tag?')
    is_account_group = fields.Boolean('Is account group?')
    is_account_expression = fields.Boolean('Is an account expression?')
    account_id = fields.Many2one('account.account', 'Account')
    group_id = fields.Many2one('account.group', 'Account group')
    tag_id = fields.Many2one('account.account.tag', 'Account tag')
    expression = fields.Char('Expression')
    tag = fields.Many2one('business.unit.tag', 'Tag')
    group = fields.Many2one('business.unit.group', 'Group')


class BusinessUnitTag(models.Model):
    _name = 'business.unit.tag'
    name = fields.Char('Name')


class BusinessUnitGroup(models.Model):
    _name = 'business.unit.group'
    name = fields.Char('Name')


class BusinessUnitReportLayout(models.Model):
    _name = 'business.unit.report.layout'

    name = fields.Char('Name')
    sequence = fields.Integer(string='Sequence', default=10)
    type = fields.Selection([
        ('group', 'Group'),
        ('tag', 'Tag'),
        ('tittle', 'Tittle'),
        ('total', 'Total'),
        ('overhead', 'Overhead'),
    ],
        string='Type', default='group')
    group = fields.Many2one('business.unit.group', 'Group')
    tag = fields.Many2one('business.unit.tag', 'Tag')
    formula = fields.Text('Formula')
    sign = fields.Boolean('Sign')
    business_unit_mapping_id = fields.Many2one('business.unit.mapping', string='Business Unit Mapping',
                                               ondelete="cascade",
                                               index=True, required=True, auto_join=True)
