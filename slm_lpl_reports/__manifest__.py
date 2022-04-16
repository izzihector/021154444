# -*- coding: utf-8 -*-
{
    'name': "Layout Profit & Loss Reports",

    'summary': """Layout Profit & Loss Reports""",

    'description': """
        Layout Profit & Loss reports
    """,
    'version': '1.0.',
    'author': 'Fernando Flores --> fflores@xetechs.com',
    'maintainer': 'XETECHS, S.A.',
    'website': 'https://www.xetechs.com',
    'category': 'account',
    'depends': ['base', 'account', 'account_reports', 'slm_encryption_reports'],
    'license': 'AGPL-3',

    'data': [
        # 'security/ir.model.access.csv',
        'views/lpl_report_data.xml',
        'views/search_template_view.xml'
    ]
}
