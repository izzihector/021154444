{
    'name': 'POS customer credit reprot',
    'version': '15.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'POS credit report of customer',
    'author': 'Mridul',
    'company': 'iBOS',
    'maintainer': 'iBOS',
    'images': [],
    'website': 'https://www.ibos.com',
    'depends': ['base', 'point_of_sale', 'pos_credit_payment'],
    'data': [
        'views/customer_credit_report_menu.xml',
        'security/ir.model.access.csv'
    ],
    'assets': {
        'web.assets_backend': [
            'ibos_customer_credit_report/static/src/js/action_manager.js',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}


