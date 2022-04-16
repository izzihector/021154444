# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime


class DefaultCostCenterPercentage(models.Model):
    _name = 'default.cost.center.percentage'
    _rec_name = 'currnt_year'

    currnt_year = fields.Char('Year', readonly=True)
    line_ids = fields.One2many('default.cost.center.percentage.line', 'default_process_id')
    state = fields.Selection([
                             ('draft', 'Draft'),
                             ('done', 'Done'),
                             ])

    _sql_constraints = [
       ('currnt_year_uniq', 'unique (currnt_year)', "Year is already exists"),
    ]

    
    def action_done(self):
        for line in self.line_ids:
            data = {
                'ma': line.ma,
                'ragio': line.ragio,
                'cargo': line.cargo,
                'cost_group_id': line.cost_group_id.id,
                'process_flow_id': line.process_flow_id.id,
            }
            line.analytic_id.write(data)
        return self.write({'state': 'done'})

    
    def get_currnt_year(self):
        for res in self:
            currentYear = datetime.now().year
            res.currnt_year = _(currentYear) + ' - ' + _(currentYear+1)

    
    def action_get_data(self):
        line_obj = self.env['default.cost.center.percentage.line']
        analytic_obj = self.env['account.analytic.account']
        analytic_data = analytic_obj.search([])
        if analytic_data:
            for analytic in analytic_data:
                line_data = {
                             'analytic_id': analytic.id,
                             'ma': analytic.ma,
                             'ragio': analytic.ragio,
                             'cargo': analytic.cargo,
                             'cost_group_id': analytic.cost_group_id.id,
                             'process_flow_id': analytic.process_flow_id.id,
                             'default_process_id': self.id
                             }
                if not line_obj.search([('analytic_id', '=', analytic.id), ('default_process_id', '=', self.id)]):
                    line_obj.create(line_data)
                    self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        res = super(DefaultCostCenterPercentage, self).create(vals)
        res.get_currnt_year()
        return res


class DefaultCostCenterPercentageLine(models.Model):
    _name = 'default.cost.center.percentage.line'

    default_process_id = fields.Many2one('default.cost.center.percentage', 'Default Process Flow Percentage')
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    ma = fields.Float(string="MA", digits=dp.get_precision('MA'))
    ragio = fields.Float(string="Ragio", digits=dp.get_precision('Ragio'))
    cargo = fields.Float(string="Cargo", digits=dp.get_precision('Cargo'))
    cost_group_id = fields.Many2one('cost.group', string="Cost Group")
    process_flow_id = fields.Many2one('process.flow', string="Process Flow")

    
    def write(self, vals):
        res = super(DefaultCostCenterPercentageLine, self).write(vals)
        total = self.ma + self.ragio + self.cargo
        if total == 0.0:
            return res
        if total != 100:
            raise UserError(_("Total(MA+Ragio+Cargo) should be 100%"))
        data = {
            'ma': self.ma,
            'ragio': self.ragio,
            'cargo': self.cargo,
            'cost_group_id': self.cost_group_id.id,
            'process_flow_id': self.process_flow_id.id,
        }
        self.analytic_id.write(data)
        return res

    @api.model
    def create(self, vals):
        res = super(DefaultCostCenterPercentageLine, self).create(vals)
        if res:
            total = res.ma + res.ragio + res.cargo
            if total == 0.0:
                return res
            if total > 0 and total != 100:
                raise UserError(_("Total(MA+Ragio+Cargo) should be 100%"))
        return res
