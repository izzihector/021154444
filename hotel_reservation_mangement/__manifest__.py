# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).



{
    'name': 'Hotel Reservation',
    'version': '15.0.',
    'category': 'Hotel',
    'depends': [
        'account','hr','sale','crm','mail','contacts','date_range',
    ],
    'author': ' FEE LLC  ',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'data': [
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        'views/email_reservation.xml',
        'views/hotel_room.xml',
        'views/hotel.xml',
        'views/room_list.xml',
        'views/hotel_reservation.xml',
        'views/period_lead_management.xml',
        'views/room_cost_attripute.xml',
        # 'views/opportunity_reservation.xml',
        'views/reservation_invoice.xml',
        'views/room_capacity.xml',
        'views/sh_message_wizard.xml',
        # 'report/reservation_invoice.xml',
        # 'report/reservation_report.xml',
    ],
    'demo': [
        # 'demo/patient.xml',
    ],
    # 'installable': True,
	'application': True,
	# 'auto_install': False,
	'sequence':1,
}
