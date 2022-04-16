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
    'name': 'Layout Profit & Loss',
    'summary': """Layout Profit & Loss""",
    'version': '1.0.',
    'description': """
Layout Profit & Loss

""",
    'author': 'Jonathan J. Guacarán R.--> jrivero@xetechs.com',
    'maintainer': 'XETECHS, S.A.',
    'website': 'https://www.xetechs.com',
    'category': 'account',
    'depends': ['account', 'report_xlsx', 'slm_subgroup', 'slm_encryption_reports'],
    'license': 'AGPL-3',
    'data': [
            'security/ir.model.access.csv',
            'data/slm_reptemp_data.xml',
            'wizard/account_layout_profitloss_report.xml',
            'reports/report.xml',
            'reports/report_layoutprofitloss.xml',
            'views/slm_reptemp_view.xml',
            'wizard/account_balance_sheet_report.xml',
            'views/business_unit_mapping_view.xml',
            'views/encryption_mapping_view.xml',
            'views/profit_center_mapping_view.xml',
            'views/profit_center_view.xml',
            'views/slm_group_mapping_view.xml',
            'views/slm_group_total_mapping_view.xml',

        'reports/report_balancesheet.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
