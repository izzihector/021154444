# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        result = super(ProductProduct, self).name_get()
        if self._context.get('report_inventory_movement', False):
            result1 = list()
            for product in self:
                for res in result:
                    result1.append((product.id, res[1].replace('[%s]'\
                        % product.default_code, '').strip()))
            return result1
        return result

    def _get_domain_locations_new(self, location_ids, company_id=False, compute_child=True):
        if self._context.get('company_id') and not company_id:
            company_id = self._context['company_id']
        if self._context.get('location') and not location_ids:
            location_ids = self._context['location']
        return super(ProductProduct, self)._get_domain_locations_new(location_ids=location_ids,
                    company_id=company_id, compute_child=compute_child)