import requests
import json
from odoo.exceptions import ValidationError
from datetime import datetime

class RequestSender:

    @staticmethod
    def request_send_to_erp_from_odoo(self, request_operation=False):
        mrr_from_external_erp = self.env['ir.config_parameter'].sudo().get_param('ibos_erp_integration.mrr_from_external_erp')
        if mrr_from_external_erp:
            if self._name == 'stock.backorder.confirmation':
                print("Start stock.backorder.confirmation:")
                self = self.pick_ids
                stock_move_ids = self.move_ids_without_package
                print("End stock.backorder.confirmation:")
            elif self._name == 'stock.picking':
                print("stock.picking")
                stock_move_ids = self.move_ids_without_package
            elif self._name == 'stock.immediate.transfer':
                print("stock.immediate.transfer")
                self = self.pick_ids
                stock_move_ids = self.move_ids_without_package

            # check only receipts
            mrr_validation_code = self.picking_type_id.sequence_code
            if mrr_validation_code == 'IN':
                stock_picking = stock_move_ids[0]
                if stock_picking.origin:
                    purchase_order = self.env['purchase.order'].search([('name', '=', stock_picking.origin)])

                objRow = []
                if self.challan_date:
                    challan_date = str(datetime.strptime(str(self.challan_date), '%Y-%m-%d'))
                else:
                    challan_date = ""

                if self.challan_number == False:
                    challan_number = ""
                else:
                    challan_number = self.challan_number

                for stock_move_id in stock_move_ids:
                    self.message_post(body="init stock_move_id:" + str(stock_move_id.state))
                    purchase_order_line = self.env['purchase.order.line'].search([('order_id', '=', stock_move_id.origin), ('product_id', '=', stock_move_id.product_id.id)])
                    if stock_move_id.state != 'cancel':
                        row = {
                            "itemId": stock_move_id.product_id.api_origin,
                            "itemName": stock_move_id.product_id.name,
                            "uoMid": stock_move_id.product_id.uom_id.api_origin,
                            "uoMname": stock_move_id.product_id.uom_id.name,
                            "numTransactionQuantity": stock_move_id.quantity_done,
                            "monTransactionValue": purchase_order_line.price_unit * stock_move_id.quantity_done,
                            "inventoryLocationId": 189,
                            "inventoryLocationName": "Trading Goods Stock",
                            "batchId": 0,
                            "batchNumber": "",
                            "inventoryStockTypeId": 1,
                            "inventoryStockTypeName": "Open Stock",
                            "strBinNo": "",
                            "vatAmount": 0,
                            "discount": 0,
                            "purchaseRate": purchase_order_line.price_unit,
                            "salesRate": 0,  # purchase_order_line.lst_price
                            "mrpRate": "0",
                            "expiredDate": "1971-02-25"
                        }
                        objRow.append(row)

                    payload = {
                        "objHeader": {
                            "transactionGroupId": 1,
                            "transactionGroupName": "Receive Inventory",
                            "transactionTypeId": 1,
                            "transactionTypeName": "Receive For PO To Open Stock",
                            "referenceTypeId": 1,
                            "referenceTypeName": "PO (Purchase Order)",
                            "referenceId": purchase_order.api_origin,
                            "referenceCode": purchase_order.erp_po_code,
                            "accountId": purchase_order.company_id.api_origin,
                            "accountName": purchase_order.company_id.name,
                            "businessUnitId": purchase_order.branch_id.api_origin,
                            "businessUnitName": purchase_order.branch_id.name,
                            "sbuId": 57,
                            "sbuName": "Apon SBU",
                            "plantId": 68,
                            "plantName": "Apon Center",
                            "warehouseId": purchase_order.picking_type_id.warehouse_id.api_origin,
                            "warehouseName": purchase_order.picking_type_id.warehouse_id.name,
                            "businessPartnerId": purchase_order.partner_id.api_origin,
                            "parsonnelId": 0,
                            "costCenterId": -1,
                            "costCenterCode": "",
                            "costCenterName": "",
                            "projectId": -1,
                            "projectCode": "",
                            "projectName": "",
                            "comments": "",
                            "actionBy": 0,
                            "documentId": "",
                            "businessPartnerName": purchase_order.partner_id.name,
                            "gateEntryNo": "",
                            "challan": challan_number,
                            "challanDateTime": challan_date,
                            "vatChallan": self.vat_challan_number,
                            "vatAmount": self.vat_challan_amount,
                            "grossDiscount": 0,
                            "freight": 0,
                            "commission": 0,
                            "shipmentId": 0,
                            "othersCharge": 0
                        },
                        "images": [],
                        "objRow": objRow,
                        "objtransfer": {}
                    }

                self.message_post(body="stock_move_id:" + str(stock_move_id.state))
                headers = {"Content-Type": "application/json"}
                url = "https://apon.ibos.io/apon/wms/InventoryTransaction/CreateInvTransection"
                response = requests.request("POST", url, json=payload, headers=headers, verify=False)

                self.message_post(body="Log:" + str(response.text))
                self.message_post(body="payload:" + str(payload))

                json_response = json.loads(response.text)
                if json_response["statuscode"] != 200:
                    raise ValidationError("MRR is not Complete, " + str(json_response["message"]))
                else:
                    inv_ref_code = json_response['message']
                    self.update({
                        'erp_inv_received_ref': inv_ref_code
                    })

        return "true"