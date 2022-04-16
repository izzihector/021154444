from odoo import fields, models, api
import json
from odoo.exceptions import ValidationError
from ..helper.request_send_to_erp import RequestSender

class StockPicking(models.Model):
    _inherit = "stock.picking"
    erp_po_code = fields.Char('PO Code', copy=False, track_visibility="always")
    erp_inv_received_ref = fields.Char('Inventory Received Ref', copy=False, track_visibility="always")
    warehouse_id = fields.Many2one('stock.warehouse', String='Warehouse', related='picking_type_id.warehouse_id', copy=False, store=True)
    scheduled_date = fields.Datetime(string='PO Date', copy=False, readonly=True, track_visibility="always")
    challan_number = fields.Char(string='Challan Number', copy=False, track_visibility="always")
    challan_date = fields.Date(string='Challan date', copy=False, track_visibility="always")
    vat_challan_number = fields.Char(string='VAT Challan Number', copy=False, track_visibility="always")
    vat_challan_amount = fields.Float(string='VAT Challan Amount', copy=False, track_visibility="always")
    notes = fields.Char(string='Notes', copy=False, track_visibility="always")
    bill_id = fields.Integer(string='Bill ID', default=0)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    # attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'stock.picking')],
    #                                  string='Attachments')

    @api.model
    def create(self, vals):
        if vals.get("origin"):
            po = self.env['purchase.order'].search([('name', '=', vals.get("origin"))])
            vals.update({
                'erp_po_code': po.erp_po_code
            })
        return super(StockPicking, self).create(vals)


    def button_validate(self):
        stock_move_ids = self.move_ids_without_package
        for stock_move_id in stock_move_ids:
            print("product_uom_qty:", stock_move_id.product_uom_qty, "/", stock_move_id.quantity_done)
            if stock_move_id.product_uom_qty < stock_move_id.quantity_done:
                print("Gater than demand qty")
                raise ValidationError("Done quantity can't be gather then demand")

        res = super(StockPicking, self).button_validate()
        stock_move_ids = self.move_ids_without_package
        # check demand qty and done qty
        is_uom_qty_demand_as_done = True
        for stock_move_id in stock_move_ids:
            if stock_move_id.product_uom_qty > stock_move_id.quantity_done:
                is_uom_qty_demand_as_done = False
                break

        if is_uom_qty_demand_as_done:
            print("warehouse_id::", self.warehouse_id.id)
            req = RequestSender.request_send_to_erp_from_odoo(self, 'stock_picking')
            if req == "true":
                stock_move_line_ids = self.move_line_ids_without_package
                for stock_move_line_id in stock_move_line_ids:
                    stock_production_lot = self.env['stock.production.lot'].search([('name', '=', stock_move_line_id.lot_name)])
                    stock_production_lot.update({
                        'mrp_unit': stock_move_line_id.mrp_unit,
                        'price_unit': stock_move_line_id.price_unit,
                        'list_price': stock_move_line_id.list_price,
                        'expiration_date': stock_move_line_id.expiration_date,
                        'warehouse_id': self.warehouse_id.id
                    })

        # mrr_from_external_erp = self.env['ir.config_parameter'].sudo().get_param('ibos_erp_integration.mrr_from_external_erp')
        # if mrr_from_external_erp:
        #     stock_picking = self
        #     if stock_picking.origin:
        #         purchase_order = self.env['purchase.order'].search([('name', '=', stock_picking.origin)])
        #
        #     import requests
        #
        #     objRow = []
        #     stock_move_ids = self.move_ids_without_package
        #
        #     # check demand qty and done qty
        #     for stock_move_id in stock_move_ids:
        #         if stock_move_id.product_uom_qty > stock_move_id.quantity_done:
        #             return res
        #
        #     for stock_move_id in stock_move_ids:
        #         purchase_order_line = self.env['purchase.order.line'].search(
        #             [('order_id', '=', stock_move_id.origin), ('product_id', '=', stock_move_id.product_id.id)])
        #
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
        #     payload = {
        #         "objHeader": {
        #             "transactionGroupId": 1,
        #             "transactionGroupName": "Receive Inventory",
        #             "transactionTypeId": 1,
        #             "transactionTypeName": "Receive For PO To Open Stock",
        #             "referenceTypeId": 1,
        #             "referenceTypeName": "PO (Purchase Order)",
        #             "referenceId": purchase_order.api_origin,
        #             "referenceCode": purchase_order.erp_po_code,
        #             "accountId": 2,
        #             "accountName": "Akij iBOS Demonstration",
        #             "businessUnitId": purchase_order.branch_id.api_origin,
        #             "businessUnitName": purchase_order.branch_id.name,
        #             "sbuId": 57,
        #             "sbuName": "Apon SBU",
        #             "plantId": 68,
        #             "plantName": "Apon Center",
        #             "warehouseId": purchase_order.picking_type_id.warehouse_id.api_origin,
        #             "warehouseName": purchase_order.picking_type_id.warehouse_id.name,
        #             "businessPartnerId": purchase_order.partner_id.api_origin,
        #             "parsonnelId": 0,
        #             "costCenterId": -1,
        #             "costCenterCode": "",
        #             "costCenterName": "",
        #             "projectId": -1,
        #             "projectCode": "",
        #             "projectName": "",
        #             "comments": "",
        #             "actionBy": 0,
        #             "documentId": "",
        #             "businessPartnerName": purchase_order.partner_id.name,
        #             "gateEntryNo": "",
        #             "challan": "",
        #             "challanDateTime": "1985-10-14",
        #             "vatChallan": "",
        #             "vatAmount": 0,
        #             "grossDiscount": 0,
        #             "freight": 0,
        #             "commission": 0,
        #             "shipmentId": 0,
        #             "othersCharge": 0
        #         },
        #         "images": [],
        #         "objRow": objRow,
        #         "objtransfer": {}
        #     }
        #     headers = {"Content-Type": "application/json"}
        #
        #     url = "https://apon.ibos.io/apon/wms/InventoryTransaction/CreateInvTransection"
        #     response = requests.request("POST", url, json=payload, headers=headers)
        #
        #     self.message_post(body="Log:" + str(response.text))
        #     self.message_post(body="payload:" + str(payload))
        #
        #     json_response = json.loads(response.text)
        #     if json_response["statuscode"] != 200:
        #         raise ValidationError("MRR is not validate, please check PO/Internet connection")
        #     else:
        #         inv_ref_code = json_response['message']
        #         self.update({
        #             'erp_inv_received_ref': inv_ref_code
        #         })

        return res
