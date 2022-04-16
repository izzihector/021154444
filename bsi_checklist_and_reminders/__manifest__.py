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
{
    'name': "Checklist and Reminders",
    'author': 'Botspot Infoware Pvt. Ltd.',
    'category': 'Employees',
    'summary': """ To Do List for Projects, Tasks, Subtasks, and Personal use """,
    'website': 'https://www.botspotinfoware.com',
    'company': 'Botspot Infoware Pvt. Ltd.',
    'maintainer': 'Botspot Infoware Pvt. Ltd.',
    'description': """ We can create a TODO list of the Project, Tasks, Subtasks, and also for personal use. We can set its timeline and take follow-up of work actual completion time. """, 
    'version': '1.0',
    'depends': ['base', 'project', 'hr_attendance', 'hr_timesheet'],
    'data': [
             'security/ir.model.access.csv',
             'views/todo_checklist_view.xml',
             'views/todo_checklist_tags_views.xml',
            ],
    'images': ['static/description/Banner.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
