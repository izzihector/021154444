{
    'name': 'Customer Load Warehouse Wise',
    'version': '15.0.0.1',
    'summary': 'Customer load warehouse wise',
    'sequence': 20,
    'description': """ Customer load warehouse wise """,
    'category': 'Point Of Sale',
    'website': '',
    'images': [],
    'depends': ['product', 'point_of_sale'],
    'data': [
        'views/pos_config.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
            'point_of_sale.assets': [
                'pos_customer_load_warehouse/static/src/js/pos_customer_load_control.js',
            ],
            'web.assets_qweb': [
                'pos_credit_payment/static/src/xml/**/*',
            ],
        },
}
