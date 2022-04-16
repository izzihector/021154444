from odoo import fields, models, api
from ..helper.request_send_to_erp import RequestSender


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    
    def process(self):
        process = super(StockImmediateTransfer, self).process()
        RequestSender.request_send_to_erp_from_odoo(self, 'transfer')
        return process