# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "POS Customer Credit Payment Odoo App",
    "version": "15.0.0.0",
    "category": "Point of Sale",
    'summary': 'App Credit Payment on POS and adjust POS payment pos partial payment point of sale partial payment point of sales credit payment pos credit payment pos wallet payment POS customer credit payment POS Customer Wallet pos credit payment pos partial credit',
    "description": """
    BrowseInfo developed a new odoo/OpenERP module apps.
    Purpose :-
Purpose of this feature is, We have define credit to selected customer, so customer's can purchases any items according to their credit availability.


Features:-

 We have created Credit Details menu in Sales. From that we can add credit for customer.
 We have created smart button on customer form view which shows how much credit available for that customer.
 We made a credit journal in accounting for payment. Which is also show in POS configuration payment options.
 POS credit Payment, POS Debit Payment, Customer Credit on POS, POS payment with credit payment, Customer POS credit payment, POS customer Payment, Customer Credit Payment on POS, POS Credit feature, Allow Credit on POS,Point of sale credit payment, POS partial payment, POS partial credit payment, POS credit with customer, Point of sale customer credit payment.
Point of sale credit Payment, Point of sale Debit Payment, Customer Credit on point of sale, point of sale payment with credit payment, Customer point of sale credit payment, point of sale customer Payment, Customer Credit Payment on point of sale, point of sale Credit feature, Allow Credit on point of sale, point of sale partial payment, point of sale partial credit payment, point of sale credit with customer.


So Now In POS..
    pos partial payment
    partial payment from pos
    point of sale partial payment
    partial payment from point of sales
    partial credit payment from pos
    pos credit payment
    partial as credit payment
    pos partial accounting payment
    accounting partial payment from pos
    pos accounting partial payment

 Validations:-
- Can not use credit payment option if there is no customer selected. It will be raise Error popup.
- if product is not selected then It will be raise Error popup in POS.
- Customer should not pay more than its credit availablity and not more than order amount.
- Customer can use lesser amount from his credit for total order amount. And for remaining amount he/she can use another journal(payment option).
- When customer has used its credit for purchasing item than it will be automatically deducted from his credit and it will be also affected at backend of Odoo.
    Module has following features.
This Module allow the seller to recharge wallet for the customer. point of sales wallet management , wallet in pos , wallet point of sale 
    POS Customer Wallet Management
    POS Wallet Management
    point of sale Wallet Management
    point of sales Wallet management
    Customer Wallet payment with POS
    Customer wallet POS
    customer credit POS
    POS customer credit payment    
    POS Customer Wallet payment Management
    POS Wallet payment Management
    point of sale Wallet payment Management
    point of sales Wallet payment management
    wallet on POS
    wallet on point of sale
        Wallet on website and POS, pay order using wallet balance
        eCommerce Wallet payment
        payment using wallet
        wallet balance.
        shop Wallet payment
        website wallet payment
        payment wallet
        payment on website using wallet
        wallet payment method
        Wallet on website and pay order using wallet balance
        eCommerce Wallet payment
        payment using wallet
        wallet balance.
        shop Wallet payment
        website wallet payment
        payment wallet
        payment on website using wallet
        Odoo wallet payment method
        Odoo website wallet add money on wallet management
        Odoo add money on pos wallet management
        Odoo recharge wallet for website and pos
        online store wallet management
        odoo webshop wallet management
        Odoo customer wallet management for website
        Odoo customer wallet management for POS
        odoo wallet recharge on pos
        Odoo wallet recharge on Website
        Website wallet customer management
        Add credit on Wallet

        POS Customer Wallet Management
        POS Wallet Management
        point of sale Wallet Management
        point of sales Wallet management
        Customer Wallet payment with POS
        Customer wallet POS
        customer credit POS
        POS customer credit payment    
        POS Customer Wallet payment Management
        POS Wallet payment Management
        point of sale Wallet payment Management
        point of sales Wallet payment management
        wallet on POs
        wallet on point of sale
This Module allow the seller to recharge wallet for the customer. 
    POS Customer Wallet Management
    POS Wallet Management
    point of sale Wallet Management
    point of sales Wallet management
    Customer Wallet payment with POS
    Customer wallet POS
    customer credit POS
    POS customer credit payment    
    POS Customer Wallet payment Management
    POS Wallet payment Management
    point of sale Wallet payment Management
    point of sales Wallet payment management
    wallet on POs
    wallet on point of sale
    This Odoo apps allow digital wallet/e-wallet facility in Odoo eCommerce/online store/webshop and POS. 
    This Odoo module is complete features of customer digital wallet management system which manages the wallet balance, 
    pay orders and bill using e-Wallet, recharge wallet. Single wallet use on point of sale as well as on Odoo Website/Webstore. 
    ccounting entries managed properly Whenever wallet amount use for payment or recharge done for wallet as well as when first time balance allocated on wallet. 
    This Odoo apps also have automatic email send features when wallet amount will be updated i.e Recharge or payment from wallet.
    If you want to manage customer wallet on Odoo then this will be the good Odoo app for use. 
    By using this app you can easily add/update wallet balance of your customer . 
    This wallet can be used as Payment on time of pos payment and eCommerce Order Payment with specific Journal. 
    Customer wallet balance can easily shown on each customer card and on POS screen as well as on Website Wallet section. 
    So don't need to go back and check each customer's wallet balance. 
    It has feature to pay partially or fully using Wallet and rest of the payment can also able to pay using other payment method(On Both POS and Website).
    Odoo website/ecommerce store digital wallet helps client engagement increased by build community of wallet user, 
    you can attract more customers by giving offer and discount on your wallet.
    This module allow digital wallet/e-wallet facility in Odoo eCommerce also on Point of Sale as Odoo e-Wallet it is must have feature for your Odoo.
    
    -Point of sale credit payment, customer credit on POS, Point of sale Customer Credit,Cash Counter credit, Payment Credit
    -POS credit payment, Point of Sale credit payment, Credit payment on POS, POS partial payment, POS partial credit payment. POS customer partial payment.
    """,
    "author": "BrowseInfo",
    "website": "https://www.browseinfo.in",
    "price": 69.00,
    "currency": 'EUR',
    "depends": ['base', 'sale_management', 'sales_team', 'point_of_sale'],
    "data": [
        'security/ir.model.access.csv',
        'views/custom_sale_view.xml',
        'views/customer_pos_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_credit_payment/static/src/js/pos_extended.js',
            'pos_credit_payment/static/src/js/PaymentScreenWidget.js',
        ],
        'web.assets_qweb': [
            'pos_credit_payment/static/src/xml/**/*',
        ],
    },
    "auto_install": False,
    "installable": True,
    'live_test_url': 'https://youtu.be/gdU-m36km3s',
    "images": ['static/description/Banner.png'],
    'license': 'OPL-1',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
