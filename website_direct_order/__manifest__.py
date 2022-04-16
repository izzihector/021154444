# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Geminate Consultancy Services (<http://geminatecs.com>).
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
    'name': "Ecommece Direct Order",
    'version': '15.0.0.1',
    'category': 'website',
    'summary': "Geminate comes with an amazing feature for creating direct orders from websites. portal customers can directly add multiple products by search with their name, SKU or barcode and select them. even they can add special notes for their product based on their special requirement.",
    'description': """
       Geminate comes with an amazing feature for creating direct orders from websites. portal customers can directly add multiple products by search with their name, SKU or barcode and select them. even they can add special notes for their product based on their special requirement.
       Additionally we allow them to save their direct order as 'Template' so in future they can reuse it for quick direct order instead of adding the same list of products manually again.
       We allow them to remove product or edit product qty even after the order is saved until it is confirmed. once it is the final order, customers can confirm it from the website itself. 
    """,
    'author': "Geminate Consultancy Services",
    'website': 'http://www.geminatecs.com',
    "depends": [
        'website_sale',
        'sale_management',
    ],
    "data": [
        'security/direct_order_security.xml',
        'data/website_data.xml',
        'views/sale_order_template.xml',
        'views/template.xml',
        'views/portal_direct_order.xml',
    ],
    "images": ['static/description/banner.png'],
    "test": [],
    'assets': {
        'web.assets_frontend': [
            'website_direct_order/static/src/js/direct_order.js',
            'website_direct_order/static/src/js/select2.min.js',
        ],
    },
    "installable": True,
    'price': 149.99,
    'currency': 'EUR'
}
