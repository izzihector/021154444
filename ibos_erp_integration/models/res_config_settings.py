# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mrr_from_external_erp = fields.Boolean("MRR From External ERP", default=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()

        mrr_from_external_erp = True if ir_config.get_param('ibos_erp_integration.mrr_from_external_erp') == "True" else False

        res.update(
            mrr_from_external_erp=mrr_from_external_erp
        )
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('ibos_erp_integration.mrr_from_external_erp', self.mrr_from_external_erp)
        super(ResConfigSettings, self).set_values()


