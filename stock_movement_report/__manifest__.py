# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inventory Movement Report (Onscreen, Excel and PDF)',
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Inventory Movement Report (Onscreen, Excel and PDF)',
    'depends': ['stock_account'],
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'description': """ Inventory movement report

    stock
    inventory
    movement
    report
    warehouse

""",
    'data': [
        'views/inventory_movement_report_views.xml',
        'views/res_config_settings_views.xml',
        'report/report_inventory_movement_templates.xml',
    ],
    'images': ['static/description/main_screen.png'],
    'assets': {
        'web.assets_backend': [
                '/web/webclient/actions/action_service',
                '/stock_movement_report/static/src/scss/inventory_movement_report.scss',
                '/stock_movement_report/static/src/js/inventory_movement_action.js',
                '/stock_movement_report/static/src/js/action_manager_stock_reports.js',
                ],
        'web.assets_qweb': [
            'stock_movement_report/static/src/xml/**/*',
        ],
        },
    'price': 149.0,
    'currency': 'EUR',
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
