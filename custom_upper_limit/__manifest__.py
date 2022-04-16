{
    'name': 'Custom Upper Limit',
    'version': '1.0.0',
    'category': 'Account',
    'sequence': 15,
    'author': 'Justo Rivera --> justo.rivera@xetechs.com',
    'summary': 'Limit accounting moves to upper an bottom date limits',
    'description': "",
    'depends': ['account'],
    'data': [
        'views/view_account_change_lock_date.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}
