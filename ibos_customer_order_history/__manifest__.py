{
    'name': 'Customer order history',
    'version': '15.0.0.0',
    'author': 'iBOS Limited',
    'summary': 'Customer order history',
    'description': """Customer order history""",
    'category': 'Customer History',
    'website': 'https://ibos.io/',
    'license': 'AGPL-3',

    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/customer_order_history_menu.xml',
        'widget/customer_history.xml',
        'report/customer_details_report.xml',
        'report/customer_report.xml',
        'security/ir.model.access.csv'
    ],
    'qweb': [],
    'images': ['static/description/Banner.png'],
    'assets': {
        'point_of_sale.assets': []
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}