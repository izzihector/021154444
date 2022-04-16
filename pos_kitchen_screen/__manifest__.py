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
  "name"                 :  "Pos Kitchen Screen",
  "summary"              :  "This is the base module for other modules related to the Pos Kitchen Screen Base. User can visualize all the kitchen related requirements on a screen inside kitchen.",
  "category"             :  "Point Of Sale",
  "version"              :  "1.2",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """Pos Kitchen Screen,order on kitchen, order on screen, order screen, screen order, items screen, items on screen, items on kitchen
                                kitchen items,product on screen, product in kitchen, kitchen products, product screen
                            """,
  "live_test_url"        :  "https://odoodemo.webkul.com/?module=pos_kitchen_screen&custom_url=/pos/web/",
  "depends"              :  [
                             'point_of_sale','web'
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/pos_kitchen_screen.xml',
                             'views/pos_kitchen_screen_views.xml',
                            # 'views/template.xml',
                            ],
 "assets"               : {

                			'point_of_sale.assets':
                					 ['pos_kitchen_screen/static/src/js/main.js',
                					   'pos_kitchen_screen/static/src/js/screens.js',
                                       'pos_kitchen_screen/static/lib/css/pos.css'
                						],
                			'web.assets_qweb': [
                				    'pos_kitchen_screen/static/src/xml/**/*',
                				],
                                'pos_kitchen_screen.display_assets':[
                                'pos_kitchen_screen/static/lib/js/kitchen_screen.js',
                                'pos_kitchen_screen/static/lib/css/main.css',
                                'web/static/lib/Chart/Chart.js'
                                ],
                						    },
  #"qweb"                 :  [
    #                          'static/src/xml/pos_screen_templates.xml',
    #                          'static/src/xml/pos_kitchen_templates.xml',
    #                        ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  199,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
