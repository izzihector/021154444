# -*- coding: utf-8 -*-
{
    'name': "POS Sales Details Advance Report",

    'summary': """
        Add cost price, sales prices and profit to POS Sales Details report
        """,

    'description': """
        Add cost price, sales prices and profit to POS Sales Details report
    """,

    'author': "da Ti Soft Consulting",
    'website': "https://github.com/trinanda",
    'images': ['static/description/icon.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_salesdetails.xml',
    ],
}
