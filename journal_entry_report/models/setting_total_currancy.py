from odoo import models, fields, api, _
from num2words import num2words


class JournalItemReportReportView(models.AbstractModel):
    _name = "report.journal_entry_report.report_journal_entries"
    _description = "Journal Entry Customer Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        domains = []
        entries = self.env['account.move.line'].search(domains, order='name asc')
        for entry in entries:
            text = num2words(entry.debit,)
            if self.env.lang == 'en_US':
                text = num2words(entry.debit, lang='en_US') + _("only")
            if self.env.lang == 'ar_001':
                text = num2words(entry.debit, lang='ar_001') + _("ريال سعودي فقط لاغير")
            docs.append({
                'date': entry.date,
                'company': entry.company_id.name,
                'journal_id': entry.journal_id.name,
                'move_id': entry.move_id.name,
                'name': entry.name,
                'debit': entry.debit,
                'credit': entry.credit,
                'partner_id': entry.partner_id.name,
                'account_id': entry.account_id.name,
                'total_debit': text
            })
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': docs,
            }
