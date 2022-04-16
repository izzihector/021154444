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
    'name': 'Invoice Custom Fields Flight SLM',
    'summary': """INVOICE Custom Fields SLM""",
    'version': '1.0.',
    'description': """
Import Data
    * Custom fields for the Customer Invoice & Vendor Invoice
    * Custom fields for Account Move Line
""",
    'author': 'Luis Aquino --> laquino@xetechs.com',
    'maintainer': 'XETECHS, S.A.',
    'website': 'https://www.xetechs.com',
    'category': 'account',
    'depends': ['base', 'account', 'slm_custom_field', 'branch'],
    'license': 'AGPL-3',
    'data': [
            'security/res_groups.xml',
            'views/account_invoice_view.xml',
    ],
    'demo': [],
    'sequence': 2,
    'installable': True,
    'auto_install': False,

}
