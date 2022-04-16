# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProfitCenterMapping(models.Model):
    _name = 'profit.center.mapping'

    name = fields.Char('Name')
    profit_center_reports = fields.One2many('profit.center.report', 'profit_center_mapping_id',
                                            string='Profit Center Report Names', copy=True)
    line_ids = fields.One2many('profit.center.mapping.line', 'profit_center_mapping_id',
                               string='Profit Center Mapping lines', copy=True)
    layout_lines = fields.One2many('profit.center.report.layout', 'profit_center_mapping_id',
                                   string='Profit Center Layout Lines', copy=True)
    break_layout_lines = fields.One2many('profit.center.report.break.layout', 'profit_center_mapping_id',
                                         string='Profit Center Break Layout Lines', copy=True)


class ProfitCenterReport(models.Model):
    _name = 'profit.center.report'

    name = fields.Many2one('profit.center', 'Profit Center')
    profit_center = fields.Many2one('account.analytic.account', 'Profit Center account')
    overhead = fields.Float('Overhead percentage')
    profit_center_mapping_id = fields.Many2one('profit.center.mapping', string='Profit Center Mapping',
                                               ondelete="cascade",
                                               index=True, required=True, auto_join=True)
    break_report = fields.Boolean('Break Report')


class ProfitCenterMappingLine(models.Model):
    _name = 'profit.center.mapping.line'

    profit_center_mapping_id = fields.Many2one('profit.center.mapping', string='Profit Center Mapping',
                                               ondelete="cascade",
                                               index=True, required=True, auto_join=True)
    is_analytical_account = fields.Boolean('Is analytical account?')
    account_id = fields.Many2one('account.account', 'Account')
    analytical_account_id = fields.Many2one('account.analytic.account', 'Analytical Account')
    tag = fields.Many2one('profit.center.tag', 'Tag')
    group = fields.Many2one('profit.center.group', 'Group')
    partial_values = fields.One2many('profit.center.mapping.line.partial.value', 'profit_center_mapping_line_id',
                                     string='Profit Center Mapping Partial Values', copy=True)
    excluded_account_tag = fields.Many2one('account.account.tag', 'Excluded Account tag')


class ProfitCenterMappingLinePartialValue(models.Model):
    _name = 'profit.center.mapping.line.partial.value'

    profit_center_mapping_line_id = fields.Many2one('profit.center.mapping.line', string='Profit Center Mapping Line',
                                                    ondelete="cascade",
                                                    index=True, required=True, auto_join=True)
    value = fields.Float('Percentage value')
    report = fields.Many2one('profit.center.report', 'Report')


class ProfitCenterTag(models.Model):
    _name = 'profit.center.tag'
    name = fields.Char('Name')


class ProfitCenterGroup(models.Model):
    _name = 'profit.center.group'
    name = fields.Char('Name')


class ProfitCenterReportLayout(models.Model):
    _name = 'profit.center.report.layout'

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
    group = fields.Many2one('profit.center.group', 'Group')
    tag = fields.Many2one('profit.center.tag', 'Tag')
    formula = fields.Text('Formula')
    sign = fields.Boolean('Sign')
    profit_center_mapping_id = fields.Many2one('profit.center.mapping', string='Profit Center Mapping',
                                               ondelete="cascade",
                                               index=True, required=True, auto_join=True)


class ProfitCenterReportBreakLayout(models.Model):
    _name = 'profit.center.report.break.layout'

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
    group = fields.Many2one('profit.center.group', 'Group')
    tag = fields.Many2one('profit.center.tag', 'Tag')
    formula = fields.Text('Formula')
    sign = fields.Boolean('Sign')
    profit_center_mapping_id = fields.Many2one('profit.center.mapping', string='Profit Center Mapping',
                                               ondelete="cascade",
                                               index=True, required=True, auto_join=True)
