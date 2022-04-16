# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ReportBackgroundLang(models.Model):
    _name = "report.background.lang"
    _description = "Report Background Line Per Language"

    # New fields. #22260
    lang_id = fields.Many2one(
        "res.lang",
        required=True,
        string="Language",
    )
    background_pdf = fields.Binary(string="Background PDF", required=True)
    file_name = fields.Char(string="File Name")
    report_id = fields.Many2one("ir.actions.report", string="Report")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
    )
