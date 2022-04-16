# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Botspot Infoware Pvt. Ltd. <www.botspotinfoware.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from datetime import datetime, date, time, timedelta
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class TodoChecklistLine(models.Model):
    _name = 'todo.checklist.line'
    _rec_name = 'description'
    _description = 'Todo Checklist Lines'

    #state = fields.Selection([('draft','Red'), ('done','Green')], string="State", default="draft")
    is_done = fields.Boolean(string="Done")
    description = fields.Text(string="Description")
    expected_time = fields.Datetime(string="Expected Time")
    actual_time = fields.Datetime(string="Actual Time")

    todo_checklist_id = fields.Many2one('todo.checklist', string="ToDo Checklist")

    @api.onchange('is_done')
    def onchange_is_done(self):
        for record in self:
            if record.is_done == True:
                record.actual_time = fields.datetime.now()
            else:
                record.actual_time = False

class TodoChecklist(models.Model):
    _name = 'todo.checklist'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.parent.mixin']
    _description = 'Todo Checklist'

    name = fields.Char(string="Name", track_visibility='always')
    datetime = fields.Datetime(string="Assigned Time", default=lambda self: fields.datetime.now() )
    user_id = fields.Many2one('res.users', string="Assigned to", track_visibility='always')
    created_by = fields.Many2one('res.users', string="Assigned by", default=lambda self: self.env.user.id, track_visibility='always')
    description = fields.Text(string="Note")

    todo_type = fields.Selection([('project','Project'), ('task','Task'), ('subtask','Subtask'), ('personal','Personal')], string="Todo Type", track_visibility='always')
    project_id = fields.Many2one('project.project', string="Project")
    task_id = fields.Many2one('project.task', string="Task")
    subtask_id = fields.Many2one('project.task', string="Subtask")
    tag_ids = fields.Many2many('todo.checklist.tags', string="Tags")

    todo_checklist_line_ids = fields.One2many('todo.checklist.line', 'todo_checklist_id', string="ToDO Checklist Lines", track_visibility='always')

    status = fields.Selection([('draft','Draft'), ('in_progress','In Progress'), ('done','Done')], string="Status", default="draft", track_visibility='always')

    @api.onchange('todo_type')
    def onchange_todo_type(self):
        for record in self:
            if record.todo_type == 'project':
                record.task_id = False
                record.subtask_id = False
            elif record.todo_type == 'task':
                record.project_id = False
                record.subtask_id = False
            elif record.todo_type == 'subtask':
                record.project_id = False
                record.task_id = False
            else:
                record.project_id = False
                record.task_id = False
                record.subtask_id = False

