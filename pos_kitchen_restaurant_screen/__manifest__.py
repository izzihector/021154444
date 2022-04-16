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
  "name"                 :  "Pos Kitchen Restaurant Screen",
  "summary"              :  "This is the base module for other modules related to the Pos Kitchen Screen Base. User can visualize all the kitchen related requirements on a screen inside kitchen.",
  "category"             :  "Point Of Sale",
  "version"              :  "1.3.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """Pos Kitchen Screen,order on kitchen, order on screen, order screen, screen order, items screen, items on screen, items on kitchen
                                kitchen items,product on screen, product in kitchen, kitchen products, product screen
                            """,
  "depends"              :  [
                             'pos_kitchen_screen','point_of_sale'

                            ],

  "data"                 :  [
                             'views/pos_kitchen_restaurant_screen_views.xml',
                            # 'views/template.xml',
                            ],
  "assets"               : {

                 			'point_of_sale.assets':
                 					 ['pos_kitchen_restaurant_screen/static/src/js/main.js',

                 						],

                 						    },
##"qweb"                    : ['static/src/xml/popup.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "pre_init_hook"        :  "pre_init_check",
}
