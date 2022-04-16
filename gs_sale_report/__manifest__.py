# -*- coding: utf-8 -*-
{
    'name': "Global Solution Sale Report",

    'summary': """
        Global Solution Sale Report
        """,

    'description': """
        Global Solution Sale Report
    """,

    'author': "Global Solutions",
    'website': "https://GlobalSolutions.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','gs_partner_customization'],
    'data': [
        'views/company_arabic_address.xml',
        'report/sale_order_paper_format.xml',
        'report/custom_header_footer.xml',
        'report/sale_order_qutation_report.xml',
        'report/report_style.xml',
    ],
    "license": "Other proprietary",
}