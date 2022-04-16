from odoo.exceptions import UserError
from odoo import api, models, fields, exceptions,_


class ProductAveragePrice(models.TransientModel):
    _name = 'items.average.price.wizard'

    report_for = [("all", "all items"),
                  ("select", "select items"), ]

    report_for = fields.Selection(report_for, string="Report For", default='all')
    date_from = fields.Date(required=True, string="Date From")
    date_to = fields.Date(required=True, string="Date To")
    product_ids = fields.Many2many('product.template', string="Products")

    def _build_contexts(self, data):
        result = {}
        result['product_ids'] = 'product_ids' in data['form'] and data['form']['product_ids'] or False
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        return result

    @api.multi
    def make_report(self):
        if self.report_for == 'select':
            domain_results = self.env['account.invoice.line'].search(
                [('product_id', 'in', self.product_ids.ids)])
        else:
            domain_results = self.env['account.invoice.line'].search([])
            self.product_ids = self.env['product.template'].search([])

        print(domain_results.ids, "domain")
        print(domain_results)
        print(len(domain_results), "length")
        if len(domain_results) >= 1:
            self.ensure_one()
            data = {}
            data['ids'] = self.env.context.get('active_ids', domain_results.ids)
            data['model'] = self.env.context.get('active_model', 'account.invoice.line')
            data['form'] = self.read(['date_from', 'date_to',  'product_ids'])[0]
            used_context = self._build_contexts(data)
            print(used_context)
            data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
            return self.with_context(discard_logo_check=True)._print_report(data)
        else:
            raise exceptions.ValidationError(
                _('Warning! There is no records to print from this search'))

    def _print_report(self, data):
        data['form'].update(self.read(
            ['product_ids', ])[0])
        # products = self.env['account.invoice.line'].browse(data['product_ids'])
        return self.env.ref('product_report.action_product_avr_price').report_action([], data=data)



class CouponReport(models.AbstractModel):
    _name = 'report.product_report.product_avr_price_template'
    _description = 'product AVG Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('product_report.product_avr_price_template')
        self.model = data['model']
        selected_modules = self.env[self.model].browse(data['ids'])
        print(selected_modules)
        return {
            'doc_ids': selected_modules.ids,
            'doc_model':  self.model,
            'data':data,
            'docs': selected_modules,

        }
