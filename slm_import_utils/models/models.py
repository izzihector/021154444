# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class slm_import_utils(models.Model):
#     _name = 'slm_import_utils.slm_import_utils'


class SlmData(models.Model):
    _name = 'slm_edgard'
    _description = 'Table for import data'

    company_id = fields.Text(string="", required=False, )
    day_book = fields.Text(string="", required=False, )
    piece_number = fields.Text(string="", required=False, )
    registration_number = fields.Text(string="", required=False, )
    book_year = fields.Text(string="", required=False, )
    period = fields.Text(string="", required=False, )
    date = fields.Datetime(string="", required=False, )
    account_number = fields.Text(string="", required=False, )
    cost_center = fields.Text(string="", required=False, )
    invoice_number = fields.Text(string="", required=False, )
    description = fields.Text(string="", required=False, )
    currency_code = fields.Text(string="", required=False, )
    branch_code = fields.Text(string="", required=False, )
    amount = fields.Float(string="",  required=False, )
    amount_srd = fields.Float(string="",  required=False, )
    amount_usd = fields.Float(string="",  required=False, )
    operation_code = fields.Text(string="", required=False, )
    date_read = fields.Datetime(string="", required=False, )
    ticketnumber = fields.Text(string="", required=False, )
    flight_number = fields.Text(string="", required=False, )
    gallon = fields.Text(string="", required=False, )
    place_code = fields.Text(string="", required=False, )
    handling = fields.Text(string="", required=False, )
    meal = fields.Text(string="", required=False, )
    passengers = fields.Text(string="", required=False, )
    man_days = fields.Text(string="", required=False, )
    s_date = fields.Text(string="", required=False, )
    cost_center_6 = fields.Text(string="", required=False, )
    cost_center_7 = fields.Text(string="", required=False, )
    personne = fields.Text(string="", required=False, )
    purchase = fields.Text(string="", required=False, )
    gallon_pr = fields.Text(string="", required=False, )
    current_day = fields.Text(string="", required=False, )
    current_month = fields.Text(string="", required=False, )
    current_year = fields.Text(string="", required=False, )
    invoice_day = fields.Text(string="", required=False, )
    invoice_month = fields.Text(string="", required=False, )
    invoice_year = fields.Text(string="", required=False, )
    air_plane_type = fields.Text(string="", required=False, )
    air_plane_registration = fields.Text(string="", required=False, )
    creditors = fields.Text(string="", required=False, )
    debtors = fields.Text(string="", required=False, )
    sheet_name = fields.Text(string="", required=False, )
    row_count = fields.Integer(string="", required=False, )
    flag = is_new_field = fields.Boolean(string="", required=False, )
    controlle = fields.Text(string="", required=False, )
    pnrr = fields.Text(string="", required=False, )
