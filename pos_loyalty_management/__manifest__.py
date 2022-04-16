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
  "name"                 :  "POS Loyalty & Rewards Program",
  "summary"              :  """Provide loyalty points on every purchase to your customers with some redemption benefits in Point Of Sale.""",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/OpenERP-POS-Loyalty-Management.html",
  "description"          :  """http://webkul.com/blog/odoo-pos-loyalty-management/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_loyalty_management&custom_url=/pos/auto",
  "depends"              :  [
                             'point_of_sale',
                             'wk_wizard_messages',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/ir_sequence_data.xml',
                             'data/product.xml',
                             'views/pos_loyalty_management_view.xml',
                             'views/pos_loyalty_history_view.xml',
                             'views/templates.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "active"               :  False,
  "application"          :  True,
  "installable"          :  True,
  "assets"               :  {
        'point_of_sale.assets': [
            "/pos_loyalty_management/static/src/css/pos_loyalty.css",
            "/pos_loyalty_management/static/src/js/PaymentScreen.js",
            "/pos_loyalty_management/static/src/js/CustomerRedeemButton.js",
            "/pos_loyalty_management/static/src/js/LoyaltyRedeemPopupWidget.js",
            "/pos_loyalty_management/static/src/js/WkLoyaltyAlertPopUp.js",
            "/pos_loyalty_management/static/src/js/pos_loyalty.js",
          ],
          'web.assets_qweb': [
            'pos_loyalty_management/static/src/xml/pos_loyalty.xml',
        ],
          },  
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}