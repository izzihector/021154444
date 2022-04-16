# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020-Today Xetechs C.A.
#    (<http://www.xetechs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


{
    'name': 'Journal Entries XLS',
    'version': '15.0',
    'category': 'account',
    'sequence': 10,
    'summary': 'Journal Entries XLS',
    'description': """
        Export Journal entries to excel through and action menu
    """,
    'author': "Fernando Flores --> fflores@xetechs.com",
    'website': "http://www.xetechs.com",
    'depends': ['base', 'account', 'report_xlsx'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/report_menu.xml',
        'views/templates.xml',
    ],
    'license': 'AGPL-3',
}