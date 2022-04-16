# -*- coding: utf-8 -*-            print("Execited")
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payment Type Report',
    'version': '1.1',
    'summary': 'ibos_pos_payment_method_report',
    'sequence': 10,
    'description': """ """,
    'category': 'Test',
    'website': '',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/PaymentTypeReport.xml',
        'views/menu.xml',
        'report/report.xml',
        'report/report_payment_method.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}