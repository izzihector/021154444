{
    "name": "Branch Customized by iBOS",
    "summary": """ Inventory Management """,
    "category": "HR Employees",
    "images": [],
    "version": "15.0.0.0.0",
    "application": False,
    "author": "iBOS Limited, Kamrul Hasan",
    "support": "info@ibos.io",
    "website": "https://ibos.io",
    "license": "Other OSI approved licence",  # MIT
    "depends": ["base", "point_of_sale", "account", "hr", "branch"],
    "data": [
        'security/branch_security.xml',
        'views/pos_config_extend.xml',
        'views/pos_order_extend.xml',
    ],
    "qweb": [
    ],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}