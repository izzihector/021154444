# -*- coding: utf-8 -*-
{
    'name': "Global Solution Invoice PDF Report",

    'summary': """
        Global Solution Invoice PDF Report
        """,

    'description': """
        Global Solution Invoice PDF Report
    """,

    'author': "Global Solutions",
    'website': "https://GlobalSolutions.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.0.0.9',
    # any module necessary for this one to work correctly
    # todo gs_partner_customuzaion
    'depends': ['base', 'account','l10n_sa_invoice'],
    'data': [
        #'views/company_arabic_address.xml',
        # 'views/res_config_settings_views.xml',
        'views/partner.xml',
        'views/invoice_view.xml',
        'report/sale_invoice_paper_format.xml',
        # 'report/custom_header_footer.xml',
        'report/invoice_report_manage.xml',
        'report/invoice_report.xml',
        'report/report_style.xml',

    ],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
