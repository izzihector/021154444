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
    'name': 'Import Data App EDGAR SLM',
    'summary': """Import data app EDGAR SLM""",
    'version': '1.0.',
    'description': """
Import Data

    * Import data from EDGAR database
    * Import data from MARGO database
    * Others
""",
    'author': 'Luis Aquino --> laquino@xetechs.com',
    'maintainer': 'XETECHS, S.A.',
    'website': 'https://www.xetechs.com',
    'category': 'account',
    'depends': ['base', 'account', 'slm_dbtable_adapt', 'account_accountant', 'slm_import_utils'],
    'license': 'AGPL-3',
    'data': [
            'security/ir.model.access.csv',
            'wizard/wizard_import_data_view.xml',
            'views/cron_views.xml',
            # 'views/reports.xml',
            # 'views/report_journal_book_template.xml',
            # 'views/report_general_ledger_template.xml',
    ],
    'demo': [],
    'sequence': 2,
    'installable': True,
    'auto_install': False,
}
