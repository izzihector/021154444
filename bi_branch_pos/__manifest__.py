# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Multiple Branch Unit Operation Setup with Point Of Sales in Odoo",
    "version" : "15.0.0.2",
    "category" : "Point of Sales",
    "depends" : ['base','point_of_sale','branch'],
    "author": "BrowseInfo",
    'summary': 'POS Multi Branch app user Multiple Branch Management POS Multi Branch app Multiple Unit Operating unit pos branch point of Sales Purchase branch pos branch pos branch unit branch unit pos for single company with Multi Branches multi company pos',
    "description": """
       Multiple Unit operation management for single company Multiple Branch management for single company
      multiple operation for single company branching company in odoo multiple store multiple company in odoo
    Branch for POS Branch for Sales Branch for Purchase Branch for all Branch for Accounting Branch for invoicing Branch for Payment order Branch for point of sales Branch for voucher
    Branch for All Accounting reports Branch Accounting filter Branch for warehouse branch for sale stock branch for location
  Unit for POS Unit for Sales Unit for Purchase Unit for all Unit for Accounting Unit for invoicing Unit for Payment order Unit for point of sales Unit for voucher Unit 
  unit All Accounting reports Unit Accounting filter branch unit for warehouse branch unit for sale stock branch unit for location
  Unit Operation for POS Unit Operation for Sales Unit operation for Purchase Unit operation for all Unit operation for Accounting Unit Operation for invoicing Unit operation for Payment order Unit operation for point of sales Unit operation for voucher Unit operation for All Accounting reports Unit operation Accounting filter.
  Branch Operation for POS Branch Operation for Sales Branch operation for Purchase Branch operation for all Branch operation for Accounting Branch Operation for invoicing Branch operation for Payment order Branch operation for point of sales Branch operation for voucher Branch operation for All Accounting reports Branch operation Accounting filter.
  Odoo pos multi branch POS odoo point of sale multi branch point of sales
  odoo point of sales multi branch on POS
  Odoo pos multiple branch POS odoo point of sale multiple branch point of sales
  odoo point of sales multiple branch on POS
  Odoo pos multiple-branch POS odoo point of sale multiple-branch point of sales
  odoo point of sales multiple-branch on POS
    odoo Multiple Unit operation management for single company Multiple Branch management for single company
    odoo multiple operation for single company. branching company in odoo multiple store multiple company in odoo
    odoo Branch for POS Branch for Sales Branch for Purchase Branch for all Branch for Accounting Branch for invoicing Branch for Payment order Branch for point of sales Branch for voucher 
    odoo Branch for All Accounting reports Branch Accounting filter Branch for warehouse branch for sale stock branch for location
    odoo Unit for POS Unit for Sales Unit for Purchase Unit for all Unit for Accounting Unit for invoicing Unit for Payment order
    odoo Unit for point of sales Unit for voucher Unit for All Accounting reports Unit Accounting filter
    odoo branch unit for warehouse branch unit for sale stock branch unit for location
  odoo Unit Operation for POS Unit Operation for Sales Unit operation for Purchase Unit operation for all Unit operation for Accounting 
  odoo Unit Operation for invoicing Unit operation for Payment order Unit operation for point of sales Unit operation for voucher Unit operation for All Accounting reports
  odoo Unit operation Accounting filter Branch Operation for POS Branch Operation for Sales 
  odoo Branch operation for Purchase Branch operation for all Branch operation for Accounting Branch Operation for invoicing
  odoo Branch operation for Payment order Branch operation for point of sales Branch operation for voucher Branch operation for All Accounting reports Branch operation Accounting filter.
  odoo branch helpdesk and support branch support and helpdesk
  odoo helpdesk branch helpdesk unit helpdek multiple unit helpdesk operation unit
  odoo branch crm odoo crm branch crm operating unit crm unit operation management crm multiple unit operating unit crm
  odoo branch Subscription branch contract Subscription branch management
  odoo contract branch management operating unit Subscription operating unit contract
  odoo Subscription unit management contract unit management Subscription operating unit management
  odoo contract operating unit management operating unit for company multi branch management
  odoo multi branch application multi operation unit application multi branch odoo multi branch
  odoo all in one multi branch application multi branch unit operation multi unit operation branch management
  odoo multi branches management application multi operation management operating Unit for POS operating Unit for Sales
  odoo operating Units for Purchase operating Unit for all operating Unit for Accounting operating Unit for invoicing
  odoo operating Unit for Payment order operating Unit for point of sales operating Unit for voucher operating Unit for All Accounting reports operating Unit Accounting filter.
  odoo Operating unit for picking operating unit for warehouse operating unit for sale stock operating unit for location
odoo operating-Unit Operation for POS operating-Unit Operation for Sales operating-Unit operation for Purchase operating-Unit operation for all 
odoo operating-Unit operation for Accounting operating-Unit Operation for invoicing operating-Unit operation for Payment order operating-Unit operation for point of sales 
odoo operating-Unit operation for voucher operating-Unit operation for All Accounting reports operating-Unit operation Accounting filter.
odoo multi branches management odoo branches management odoo multiple branches management on odoo branchs mananegement
odoo many branches for single company odoo

       branch helpdesk and support
       branch support and helpdesk
       helpdesk branch
       helpdesk unit
       helpdek multiple unit
       helpdesk operation unit
       branch crm
       MultiBranch
       multi company
       crm branch
       crm operating unit
       crm unit operation management
       crm multiple unit
       operating unit crm
       branch Subscription
       branch contract
       Subscription branch management
       contract branch management
       operating unit Subscription
       operating unit contract
       Subscription unit management
       contract unit management
       Subscription operating unit management
       contract operating unit management

       operating unit for company.
       multi branch management
       multi branch application
       multi operation unit application multi branch odoo multi branch
       all in one multi branch application multi branch unit operation multi unit operation branch management
       odoo multi branches management application multi operation management

operating Unit for POS,operating Unit for Sales,operating Unit for Purchase,operating Unit for all,operating Unit for Accounting,operating Unit for invoicing,operating Unit for Payment order,operating Unit for point of sales,operating Unit for voucher,operating Unit for All Accounting reports,operating Unit Accounting filter. Operating unit for picking, operating unit for warehouse, operating unit for sale stock, operating unit for location
operating-Unit Operation for POS,operating-Unit Operation for Sales,operating-Unit operation for Purchase,operating-Unit operation for all, operating-Unit operation for Accounting,operating-Unit Operation for invoicing,operating-Unit operation for Payment order,operating-Unit operation for point of sales,operating-Unit operation for voucher,operating-Unit operation for All Accounting reports,operating-Unit operation Accounting filter.
    """,
    "website" : "https://www.browseinfo.in",
    'price': 40,
    'currency': "EUR",
    "data": [
        'security/branch_pos_security.xml',
        'views/pos_branch_view.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    "auto_install": False,
    "installable": True,
    'license': 'OPL-1',
    'assets': {
        'point_of_sale.assets': [
            'bi_branch_pos/static/src/js/pos_extended.js',
        ],
        'web.assets_qweb': [
            'bi_branch_pos/static/src/xml/**/*',
        ],
    },
    'live_test_url':'https://youtu.be/f-nqKb_jELg',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
