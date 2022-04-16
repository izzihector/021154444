from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    erp_po_code = fields.Char('PO Code')
    approval_status = fields.Boolean("Approval Status", default=False)
    api_origin = fields.Char('API Origin')

    def write(self, vals):
        state = vals.get('state')
        res = super(PurchaseOrder, self).write(vals)
        print("state:", state)

        for order in self:
            if order.state == "sent":
                self.button_confirm()
        return res

    def button_confirm(self):
        return super(PurchaseOrder, self).button_confirm()
