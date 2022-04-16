# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Luis Aquino -- Xetechs, S.A.
#    Copyright (C) 2019-Today Xetechs (<https://www.xetechs.com>).
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
##############################################################################

{
    'name': 'Account Sub groups',
    'summary': """Account Sub Groups""",
    'version': '1.0.',
    'description': """
Account Sub Group

""",
    'author': 'Jonathan J. Guacarán R.--> jrivero@xetechs.com',
    'maintainer': 'XETECHS, S.A.',
    'website': 'https://www.xetechs.com',
    'category': 'account',
    'depends': ['account'],
    'license': 'AGPL-3',
    'data': [
            'data/account_subgroup_data.xml',
            'security/ir.model.access.csv',
            'views/account_subgroup_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
