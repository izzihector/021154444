# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockInternalTransferReportView(models.AbstractModel):
    _name = "report.sgeede_internal_transfer.stock_internal_transfer_view"
    _description = "Stock Internal Transfer Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        count = 1
        stock_internal = self.env['stock.internal.transfer'].search([('id', '=', docids)])
        for line in stock_internal.line_ids:
            docs.append({
                'seq': count,
                'product_id': line.product_id.name,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.name,
            })
            count += 1
            print("docs", docs)
        return {
            'docs': docs,
            'name': stock_internal.name,
            'date': stock_internal.date,
            'source_warehouse_id': stock_internal.source_warehouse_id.name,
            'dest_warehouse_id': stock_internal.dest_warehouse_id.name,

        }
