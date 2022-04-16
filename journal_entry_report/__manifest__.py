# -*- coding: utf-8 -*-
{
    'name': "JournaL Entry Report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'web'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/template.xml',
        'reports/paper_format_journal_entry.xml',
        'reports/custom_header_footer.xml',
        'reports/journal_entry_report.xml',

        'reports/payment_paper_format.xml',
        'reports/custom_header_footer_payment.xml',
        'reports/payment_receipt_inherit.xml',
        'reports/account_payment.xml',
        'reports/report_style.xml',
    ],
}
