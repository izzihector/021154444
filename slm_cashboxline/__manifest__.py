# -*- encoding: UTF-8 -*-
##############################################################################
#
##############################################################################
{
    'name': 'CashSession Report CashBoxLine',
    'summary': """Print Report Coins Cashbox Session""",
    'version': '',
    'description': """Print Report Coins Cashbox Session""",
    'author': 'Xetechs S.A',
    'maintainer': 'Xetechs S.A',
    'website': 'https://www.xetechs.com',
    'category': 'account',
    'depends': ['account', 'cash_session'],
    'license': 'AGPL-3',
    'data': [
            'reports/slm_cashboxline.xml',
            # 'reports/purchase_book_report.xml',
            # 'reports/cashboxline_pdf_menu.xml'
             ],
    'demo': [],
    # 'images': ['static/description/banner.jpg'],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,

}
