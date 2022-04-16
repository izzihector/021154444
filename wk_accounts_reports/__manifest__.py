# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name": "Gs Trial Balance Customization",
    "summary": """Trial Balance Customization""",
    "category": "Accounting",
    "version": "1.0.0",
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://store.webkul.com/",
    "description": """Account Report Trial Balance Customization""",
    "live_test_url": "",
    "depends": [
        'account_reports',
    ],
    "data": [
        'views/assets.xml',
    ],
    "images": ['static/description/Banner.png'],
    "application": True,
    "installable": True,
    "auto_install": False,
    "price": 0,
    "currency": "USD",
    "pre_init_hook": "pre_init_check",
    'assets': {
      'web.assets_backend': [
        'wk_accounts_reports/static/src/js/report.js',
      ],
    },
}
