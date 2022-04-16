# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Luis Aquino -- Xetechs, S.A.
#    Copyright (C) 2019-Today Xetechs (<https://www.xetechs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from odoo import models, fields
import base64


class WizardDataImport(models.TransientModel):
    _name = "wizard.data.import"
    _description = "Wizard data import from external apps"

    company_id = fields.Many2one(
        'res.company', 'Company', required=True, default=lambda self: self.env.user.company_id)
    no_rows = fields.Integer('Number of Transactions', readonly=True)
    notes = fields.Text('Log')
    txt_filename = fields.Char('File', required=False, readonly=True)
    file = fields.Binary('File', required=False, readonly=True)
    type_transactions = fields.Selection([
        ('edgar_app', 'Transactions from EDGAR'),
        ('margo_app', 'Transactions from MARGO'),
        ('elavon_app', 'Transactions from ELAVON'),
        ('delete_table', 'Delete data table')], string="Type transactions", default="edgar_app")

    def action_search_rows(self):
        cr = self.env.cr
        num_rows = 0
        if self.type_transactions == 'edgar_app':
            sql = ('''select count(id) as trans from slm_edgard se;''')
            cr.execute(sql, [])
            for row in cr.dictfetchall():
                num_rows += row['trans']
            # if num_rows > 0:
            self.write({
                'no_rows': int(num_rows),
            })
        elif self.type_transactions == 'margo_app':
            sql = (
                '''select count(sm.id) as number from slm_edgard sm where sm.sheet_name != 'SALES JOURN';''')
            cr.execute(sql, [])
            for row in cr.dictfetchall():
                num_rows += row['number']
            # if num_rows > 0:
            self.write({
                'no_rows': int(num_rows),
            })
        elif self.type_transactions == 'delete_table':
            sql = ('''select count(sm.id) as number from slm_edgard sm;''')
            cr.execute(sql, [])
            for row in cr.dictfetchall():
                num_rows += row['number']
            # if num_rows > 0:
            self.write({
                'no_rows': int(num_rows),
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Data import from external apps',
            'res_model': 'wizard.data.import',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def action_update_rows(self):
        log_file = False
        invoice_obj = self.env['account.move']
        # try:
        if self.type_transactions == 'edgar_app':
            invoice_obj.create_invoice_edgar()
            log_file = invoice_obj.create_move_margo()

        if 'warning' in log_file:
            # to close the current active wizard
            # open the new success message box
            view = self.env.ref('sh_message.sh_message_wizard')
            context = dict(self._context or {})
            context['message'] = log_file['warning']
            return {
                'name': 'Import failure',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sh.message.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context,
            }
        if log_file:
            self.write({
                'txt_filename': '%s:%s.txt' % ('log_import', fields.Datetime.now()),
                'file': base64.b64encode(bytes(log_file, 'utf-8')),
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Data import from external apps',
            'res_model': 'wizard.data.import',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
            # 'warning': log_file['warning']
        }

    def action_delete_rows(self):
        cr = self.env.cr
        if self.no_rows:
            sql = ('''delete from slm_edgard;''')
            cr.execute(sql, [])
        return True


WizardDataImport()
