# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
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
    'name': 'Force Invoice Number',
    'version': '15.0.0.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Allows to force invoice number on specific invoices',
    'author': 'Laxicon Solution',
    'website': 'http://www.laxicon.in',
    'license': 'AGPL-3',
    'depends': [
        'account'
    ],
    'data': [
        'security/security.xml',
        # 'views/account_invoice_view.xml'
    ],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,
}
