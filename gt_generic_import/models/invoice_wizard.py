# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import exceptions, fields, models, _
import base64
import xlrd
import io
from odoo.tools import pycompat
from odoo.exceptions import ValidationError
from datetime import datetime


class Invoice_wizard(models.TransientModel):
    _name = 'invoice.wizard'

    select_file = fields.Selection(
        [('csv', 'CSV File'), ('xls', 'XLS File')], string='File Type')
    data_file = fields.Binary(string="File")
    state = fields.Selection([('draft', 'Import Draft Invoice'),
                              ('validate', 'Validate')], string='Invoice Stage Option')
    seq_opt = fields.Selection([('s_sequence', 'Use System Default Sequence Number'), ('f_sequence',
                                                                                       'Use Excel/CSV Sequence Number. (If use this option you will not able to delete it even if it is in a draft state.)')], string='Sequence Option')
    type = fields.Selection(
        [('out_invoice', 'Customer'), ('in_invoice', 'Supplier')], string='Type')
    account_option = fields.Selection([('a_account', 'Use Account From Configuration Product/Category'),
                                       ('a_excel', 'Use Account From Excel/CSV')], string='Account Option')
    imp_product_by = fields.Selection([('barcode', 'Barcode'), ('code', 'Code'), ('name', 'Name')],
                                      string='Import Product By')
    option = fields.Selection(
        [('create', 'Create'), ('skip', 'Skip ')], string='Operation')

    def Import_customer_invoice(self):
        Partner = self.env['res.partner']
        Log = self.env['log.management']
        Currency = self.env['res.currency']
        Product = self.env['product.product']
        Uom = self.env['uom.uom']
        Tax = self.env['account.tax']
        User = self.env['res.users']
        Team = self.env['crm.team']
        Account = self.env['account.account']
        Account_type = self.env['account.account.type']
        Term = self.env['account.payment.term']
        Uom_categ = self.env['uom.category']
        inv_result = {}

        invoice_obj = self.env['account.move']
        invoice_obj_fileds = invoice_obj.fields_get()
        inv_default_value = invoice_obj.default_get(invoice_obj_fileds)

        invoice_line_obj = self.env['account.move.line']
        line_fields = invoice_line_obj.fields_get()
        invline_default_value = invoice_line_obj.default_get(line_fields)

        file_data = False
        if self.option and self.state and self.select_file and self.data_file and self.seq_opt and self.type and self.account_option and self.imp_product_by:
            try:
                if self.select_file == 'csv':
                    csv_reader_data = pycompat.csv_reader(io.BytesIO(
                        base64.decodestring(self.data_file)), quotechar=",", delimiter=",")
                    csv_reader_data = iter(csv_reader_data)
                    next(csv_reader_data)
                    file_data = csv_reader_data
                elif self.select_file == 'xls':
                    file_datas = base64.decodestring(self.data_file)
                    workbook = xlrd.open_workbook(file_contents=file_datas)
                    sheet = workbook.sheet_by_index(0)
                    data = [[sheet.cell_value(r, c) for c in range(
                        sheet.ncols)] for r in range(sheet.nrows)]
                    data.pop(0)
                    file_data = data
            except:
                raise exceptions.Warning(_('Please select proper file type.'))
        else:
            raise exceptions.Warning(
                _('Please select all the required fields.'))
        for row in file_data:
            if len(row) != 15 and self.select_file == 'csv':
                raise ValidationError(
                    "You can let empty cell in csv file or please use xls file.")
            if not row[1] or not row[0] or not row[8]:
                raise exceptions.Warning(
                    _('Invoice Number,Partner,Product values are required.'))
            inv_obj_update = inv_default_value.copy()

#            Partner
            if self.type == 'out_invoice':
                partner_id = Partner.search(
                    [('name', '=ilike', row[1]), ('active', '=', True), ('customer', '=', True)], limit=1)
            else:
                partner_id = Partner.search(
                    [('name', '=ilike', row[1]), ('active', '=', True), ('supplier', '=', True)], limit=1)
            if partner_id:
                partner_id = partner_id.id
            else:
                if self.option == 'create':
                    if self.type == 'out_invoice':
                        partner_id = Partner.create(
                            {'name': row[1], 'customer': True, 'supplier': False, 'company_type': 'company'}).id
                    else:
                        partner_id = Partner.create(
                            {'name': row[1], 'supplier': True, 'customer': False, 'company_type': 'company'}).id
                else:
                    Log.create(
                        {'operation': 'inv', 'message': 'Skipped could not find the partner with name %s' % str(row[1])})
                    continue
#           Currency
            if row[2]:
                currency_id = Currency.search(
                    [('name', '=ilike', row[2])], limit=1)
                if currency_id:
                    currency_id = currency_id.id
                else:
                    if self.option == 'create':
                        currency_id = Currency.create(
                            {'name': row[2], 'symbol': '$'}).id
                    else:
                        Log.create(
                            {'operation': 'inv', 'message': 'Skipped could not find the currency with name %s' % str(row[2])})
                        continue
                inv_obj_update.update({'currency_id': currency_id})
#           Salesperson
            user_id = False
            if row[4]:
                user_id = User.search([('name', '=ilike', row[4])], limit=1)
                if user_id:
                    user_id = user_id.id
                else:
                    if self.option == 'create':
                        user_id = User.create(
                            {'name': row[4], 'login': row[4].lower()}).id
                    else:
                        Log.create(
                            {'operation': 'inv', 'message': 'Skipped could not find the salesperson with name %s' % str(row[4])})
                        continue

#           Search if not found it will create if create option is selected
            team_id = False
            if row[5]:
                team_id = Team.search([('name', '=ilike', row[5])], limit=1)
                if team_id:
                    team_id = team_id.id
                else:
                    if self.option == 'create':
                        team_id = Team.create(
                            {'name': row[5], 'team_type': 'sales'}).id
                    else:
                        Log.create(
                            {'operation': 'inv', 'message': 'Skipped could not find the sales team with name %s' % str(row[5])})
                        continue

#           Search if not found it will create if create option is selected
            payment_term_id = False
            if row[6]:
                payment_term_id = Term.search(
                    [('name', '=ilike', row[6])], limit=1)
                if payment_term_id:
                    payment_term_id = payment_term_id.id
                else:
                    if self.option == 'create':
                        payment_term_id = Term.create({'name': row[6]}).id
                    else:
                        Log.create(
                            {'operation': 'inv', 'message': 'Skipped could not find the payment term with name %s' % str(row[6])})
                        continue
            try:
                date = datetime.strptime(
                    row[3], '%d-%m-%Y').strftime('%Y-%m-%d')
            except:
                raise exceptions.Warning(_('Date format must be dd-mm-yyyy.'))

            inv_obj_update.update({
                'partner_id': partner_id,
                'payment_term_id': payment_term_id,
                'user_id': user_id,
                'team_id': team_id,
                'reference': str(int(row[7])) if isinstance(row[7], float) else row[7],
                'move_name': row[0] if self.seq_opt == 'f_sequence' else '',
                'date_invoice': date,
                'type': self.type == 'out_invoice' and 'out_invoice' or 'in_invoice',
            })

            line_vals = invline_default_value.copy()

#            Search if not found it will create if create option is selected
            if self.imp_product_by == 'barcode':
                product_id = Product.search([('barcode', '=', str(int(row[8])) if isinstance(
                    row[8], float) else row[8]), ('active', '=', True)], limit=1)
            if self.imp_product_by == 'code':
                product_id = Product.search([('default_code', '=', str(int(row[8])) if isinstance(
                    row[8], float) else row[8]), ('active', '=', True)], limit=1)
            if self.imp_product_by == 'name':
                product_id = Product.search([('name', '=', str(int(row[8])) if isinstance(
                    row[8], float) else row[8]), ('active', '=', True)], limit=1)

            if not product_id:
                #                product_id=product_id.id
                #            else:
                if self.option == 'create':
                    product_id = Product.create({'list_price': row[12], 'default_code': str(int(row[8])) if isinstance(
                        row[8], float) else row[8], 'name': str(int(row[8])) if isinstance(row[8], float) else row[8], 'type': 'product'})
                else:
                    Log.create({'operation': 'inv', 'message': 'Skipped could not find the product with code %s' % str(
                        int(row[8])) if isinstance(row[8], float) else row[8]})
                    continue

#            Search if not found it will create if create option is selected
            uom_id = Uom.search([('name', '=ilike', row[10])], limit=1)
            uom_categ_id = Uom_categ.search([('name', '=', 'Unit')], limit=1)

            if uom_id:
                uom_id = uom_id.id
            else:
                if self.option == 'create':
                    uom_id = Uom.create(
                        {'name': row[10], 'category_id': uom_categ_id.id}).id
                else:
                    Log.create(
                        {'operation': 'inv', 'message': 'Skipped could not find the uom with name %s' % str(row[10])})
                    continue

#           Taxes
            taxes_ids = False
            if row[13]:
                if self.type == 'out_invoice':
                    taxes_ids = Tax.search(
                        [('name', '=', float(row[13])), ('type_tax_use', '=', 'sale')], limit=1)
                else:
                    taxes_ids = Tax.search(
                        [('name', '=', float(row[13])), ('type_tax_use', '=', 'purchase')], limit=1)
                if taxes_ids:
                    taxes_ids = taxes_ids.id
                else:
                    if self.option == 'create':
                        if self.type == 'out_invoice':
                            taxes_ids = Tax.create(
                                {'name': float(row[13]), 'type_tax_use': 'sale', 'amount': float(row[13])}).id
                        else:
                            taxes_ids = Tax.create({'name': float(
                                row[13]), 'type_tax_use': 'purchase', 'amount': float(row[13])}).id
                    else:
                        Log.create(
                            {'operation': 'inv', 'message': 'Skipped could not find the tax with name %s' % str(row[13])})
                        continue

#           Account
            if row[14] and self.account_option == 'a_excel':
                account_id = Account.search([('code', '=', str(
                    int(row[14])) if isinstance(row[14], float) else row[14])], limit=1)
                if account_id:
                    account_id = account_id.id
                else:
                    if self.option == 'create':
                        account_id = Account.create({'code': str(int(row[14])) if isinstance(row[14], float) else row[14], 'name': str(int(row[14])) if isinstance(row[14], float) else row[14], 'user_type_id': Account_type.search(
                            [('name', '=', 'Income')], limit=1).id if self.type == 'out_invoice' else Account_type.search([('name', '=', 'Expenses')], limit=1).id}).id
                    else:
                        Log.create(
                            {'operation': 'inv', 'message': 'Skipped could not find the account with code %s' % str(row[14])})
                        continue
                line_vals.update({'account_id': account_id})
            else:
                line_vals.update({'account_id': product_id.categ_id.property_account_income_categ_id.id if self.type ==
                                  'out_invoice' else product_id.categ_id.property_account_expense_categ_id.id})

            if not line_vals.get('account_id'):
                raise exceptions.Warning(
                    _('Could not find the account for product %s') % product_id.name)

            line_vals.update({
                'product_id': product_id.id,
                'name': row[11],
                'quantity': row[9],
                'uom_id': uom_id,
                'price_unit': row[12],
                'invoice_line_tax_ids': [(6, 0, [taxes_ids])],
            })
            l2 = [(0, 0, line_vals)]

            if inv_result.get(row[0]):
                l1 = inv_result[row[0]]['invoice_line_ids']
                inv_result[row[0]].update({'invoice_line_ids': l1 + l2})

            if not inv_result.get(row[0]):
                inv_obj_update.update({'invoice_line_ids': l2})
                inv_result[row[0]] = inv_obj_update
        for invoice_data in inv_result.values():
            invoice_var = invoice_obj.create(invoice_data)
            if self.state == "validate":
                invoice_var.action_invoice_open()
        return True
