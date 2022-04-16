# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Fernando Flores -- Xetechs, S.A.
#    Copyright (C) 2020-Today Xetechs (<https://www.xetechs.com>).
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
    'name': 'Budget reports SLM',
    'summary': """
        Configuration tools for mapping and report generation
    """,
    'version': '1.0.',
    'description': """
        Budget reports for SLM
        * Encryption Mapping
        * Encryption Report
        * Profit Center Report
        * Business Unit Report
        * SLM Group Total Report
    """,
    'author': 'Fernando Flores --> fflores@xetechs.com',
    'maintainer': 'XETECHS, S.A.',
    'website': 'https://www.xetechs.com',
    'category': 'account',
    'depends': ['base', 'account', 'account_reports', 'slm_encryption_reports'],
    'license': 'AGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/budget_encryption_report_data.xml',
        'views/budget_encryption_mapping_view.xml',
    ],
    'license': 'AGPL-3',
}
