# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Grant Portal Access to Contact Quick',
    'version': '1.0.0',
    'license': 'Other proprietary',
    'price': 15.0,
    'currency': 'EUR',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'summary':  """Quick Create Portal User Access for Contacts.""",
    'description': """
Quick Create Portal User Access
Create Portal User Access
Customers User Access
Vendors User Access 
Contacts User Access
Partners User Access
Quick Create Portal User Access
Grant Access
    """,
    'category': 'Sales/Sales',
    'depends': [
        'base',
        'portal',
        'mail',
    ],
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/create_user_contact_customer/1129',
    'data': [
        'data/data_view.xml',
        'views/contact_view.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
