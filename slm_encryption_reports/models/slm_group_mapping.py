# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SLMGroupTotalMapping(models.Model):
    _name = 'slm.group.total.mapping'

    name = fields.Char('Name')

    business_units = fields.Many2many('slm.group.mapping', string='SLM business unit',
                                     copy=True)
    layout_lines = fields.One2many('slm.group.report.layout', 'slm_group_total_mapping_id',
                                   string='SLM Group Layout Lines', copy=True)


class SLMGroupReportLayout(models.Model):
    _name = 'slm.group.report.layout'

    name = fields.Char('Name')
    sequence = fields.Integer(string='Sequence', default=10)
    type = fields.Selection([
        ('group', 'Group'),
        ('tag', 'Tag'),
        ('tittle', 'Tittle'),
        ('total', 'Total'),
        ('overhead', 'Overhead'),
    ],
        string='Type', default='tag')
    group = fields.Many2one('slm.group.group', 'Group')
    tag = fields.Many2one('slm.group.tag', 'Tag')
    formula = fields.Text('Formula')
    sign = fields.Boolean('Sign')
    slm_group_total_mapping_id = fields.Many2one('slm.group.total.mapping', string='SLM Group Mapping',
                                                 ondelete="cascade",
                                                 index=True, required=True, auto_join=True)


class SLMGroupMapping(models.Model):
    _name = 'slm.group.mapping'

    name = fields.Char('Name')
    line_ids = fields.One2many('slm.group.mapping.line', 'slm_group_mapping_id',
                               string='SLM Group Mapping lines', copy=True)
    profit_center = fields.Many2one('account.analytic.account', 'Profit Center account')


class SLMGroupMappingLine(models.Model):
    _name = 'slm.group.mapping.line'

    slm_group_mapping_id = fields.Many2one('slm.group.mapping', string='SLM Group Mapping',
                                           ondelete="cascade",
                                           index=True, required=True, auto_join=True)
    is_account_tag = fields.Boolean('Is account tag?')
    is_account_group = fields.Boolean('Is account group?')
    is_account_expression = fields.Boolean('Is an account expression?')
    account_id = fields.Many2one('account.account', 'Account')
    group_id = fields.Many2one('account.group', 'Account group')
    tag_id = fields.Many2one('account.account.tag', 'Account tag')
    expression = fields.Char('Expression')
    tag = fields.Many2one('slm.group.tag', 'Tag')
    group = fields.Many2one('slm.group.group', 'Group')


class SLMGroupTag(models.Model):
    _name = 'slm.group.tag'
    name = fields.Char('Name')


class SLMGroupGroup(models.Model):
    _name = 'slm.group.group'
    name = fields.Char('Name')
