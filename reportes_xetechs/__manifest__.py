# -*- coding: utf-8 -*-
{
    'name': "reportes_xetechs",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/reportes_menu.xml',
        'reports/report_invoice_surinam.xml',
        'reports/report_invoice_amsterdam.xml',
        'reports/report_invoice_belem.xml',
        'reports/report_invoice_curacao.xml',
        'reports/report_invoice_geo.xml',
        'reports/report_invoice_miami.xml',
        'reports/report_invoice_catering.xml',
        'reports/report_invoice_ground.xml',
        'reports/report_invoice_aircargo.xml',
        # 'reports/report_purchaseorder.xml',
    ],
    'license': 'AGPL-3',
}
