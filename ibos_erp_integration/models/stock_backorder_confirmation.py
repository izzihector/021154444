from odoo import fields, models, api
from ..helper.request_send_to_erp import RequestSender

class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    # def process(self):
    #     res = super(StockImmediateTransfer, self).process()
    #     RequestSender.request_send_to_erp_from_odoo(self, 'back_order')
    #     return res

    def process_cancel_backorder(self):
        res = super(StockImmediateTransfer, self).process_cancel_backorder()
        RequestSender.request_send_to_erp_from_odoo(self, 'cancel_order')
        return res

    # def process_to_erp_purchase_received(self, is_cancel=False):
    #     stock_move_ids = self.pick_ids
    #     print("stock_move_ids::", stock_move_ids)
    #     RequestSender.request_send_to_erp_from_odoo(self, stock_move_ids, is_cancel)


        # if stock_picking.origin:
        #     purchase_order = self.env['purchase.order'].search([('name', '=', stock_picking.origin)])
        #
        # import requests
        #
        # url = "https://apon.ibos.io/apon/wms/InventoryTransaction/CreateInvTransection"
        #
        # objRow = []
        # stock_move_ids = self.pick_ids.move_ids_without_package
        # print("stock_move_ids:", stock_move_ids)
        #
        # for stock_move_id in stock_move_ids:
        #     print("stock_move_id:", stock_move_id.state)
        #     purchase_order_line = self.env['purchase.order.line'].search(
        #         [('order_id', '=', stock_move_id.origin), ('product_id', '=', stock_move_id.product_id.id)])
        #     if stock_move_id.state != 'cancel':
        #         row = {
        #             "itemId": stock_move_id.product_id.api_origin,
        #             "itemName": stock_move_id.product_id.name,
        #             "uoMid": stock_move_id.product_id.uom_id.api_origin,
        #             "uoMname": stock_move_id.product_id.uom_id.name,
        #             "numTransactionQuantity": stock_move_id.quantity_done,
        #             "monTransactionValue": purchase_order_line.price_unit * stock_move_id.quantity_done,
        #             "inventoryLocationId": 189,
        #             "inventoryLocationName": "Trading Goods Stock",
        #             "batchId": 0,
        #             "batchNumber": "",
        #             "inventoryStockTypeId": 1,
        #             "inventoryStockTypeName": "Open Stock",
        #             "strBinNo": "",
        #             "vatAmount": 0,
        #             "discount": 0,
        #             "purchaseRate": purchase_order_line.price_unit,
        #             "salesRate": 0,  # purchase_order_line.lst_price
        #             "mrpRate": "0",
        #             "expiredDate": "1971-02-25"
        #         }
        #         objRow.append(row)
        #
        # payload = {
        #     "objHeader": {
        #         "transactionGroupId": 1,
        #         "transactionGroupName": "Receive Inventory",
        #         "transactionTypeId": 1,
        #         "transactionTypeName": "Receive For PO To Open Stock",
        #         "referenceTypeId": 1,
        #         "referenceTypeName": "PO (Purchase Order)",
        #         "referenceId": purchase_order.api_origin,
        #         "referenceCode": purchase_order.erp_po_code,
        #         "accountId": 2,
        #         "accountName": "Akij iBOS Demonstration",
        #         "businessUnitId": purchase_order.branch_id.api_origin,
        #         "businessUnitName": purchase_order.branch_id.name,
        #         "sbuId": 57,
        #         "sbuName": "Apon SBU",
        #         "plantId": 68,
        #         "plantName": "Apon Center",
        #         "warehouseId": purchase_order.picking_type_id.warehouse_id.api_origin,
        #         "warehouseName": purchase_order.picking_type_id.warehouse_id.name,
        #         "businessPartnerId": purchase_order.partner_id.api_origin,
        #         "parsonnelId": 0,
        #         "costCenterId": -1,
        #         "costCenterCode": "",
        #         "costCenterName": "",
        #         "projectId": -1,
        #         "projectCode": "",
        #         "projectName": "",
        #         "comments": "",
        #         "actionBy": 0,
        #         "documentId": "",
        #         "businessPartnerName": purchase_order.partner_id.name,
        #         "gateEntryNo": "",
        #         "challan": "",
        #         "challanDateTime": "1985-10-14",
        #         "vatChallan": "",
        #         "vatAmount": 0,
        #         "grossDiscount": 0,
        #         "freight": 0,
        #         "commission": 0,
        #         "shipmentId": 0,
        #         "othersCharge": 0
        #     },
        #     "images": [],
        #     "objRow": objRow,
        #     "objtransfer": {}
        # }
        #
        # headers = {"Content-Type": "application/json"}
        #
        # response = requests.request("POST", url, json=payload, headers=headers)
        #
        # print(response.text)
        #
        # self.pick_ids.message_post(body="Log:" + str(response.text))
        #
        # self.pick_ids.message_post(body="payload:" + str(payload))
        #
        # json_response = json.loads(response.text)
        # if json_response["statuscode"] != 200:
        #     raise ValidationError("MRR is not validate, please check PO/Internet connection")
        # else:
        #     inv_ref_code = json_response['message']
        #     self.pick_ids.update({
        #         'erp_inv_received_ref': inv_ref_code
        #     })