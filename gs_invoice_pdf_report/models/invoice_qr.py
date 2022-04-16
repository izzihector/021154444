# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
import qrcode, base64
from io import BytesIO

class QRCodeAddon(models.Model):
    _inherit = 'account.move'

    service_date_char = fields.Char('Service Date')

    def _post(self, soft=True):
        res = super()._post(soft)
        if self.invoice_date:
            if self.invoice_date < fields.Date.today():
                raise ValidationError(_("The Invoice Date Must Be Today Or After"))
        return res
    @api.onchange('invoice_date')
    def _onchange_date_validation(self):
        if self.invoice_date:
            if self.invoice_date < fields.Date.today():
                raise ValidationError(_("You Cannot Enter Date Before Today"))

    @api.onchange('partner_id')
    def _onchange_company_warning_vat(self):
        if self.move_type in ('out_invoice', 'out_refund'):
            if not self.env.company.vat:
                raise ValidationError(_("Please Ask The Administrator To Set Tax ID To Your Company."))

    @api.onchange('partner_id')
    def _onchange_partner_warning_vat(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        warning = {}
        if partner.company_type == 'company' and not partner.vat:
            title = ("Warning for %s") % partner.name
            message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
            warning = {
                'title': title,
                'message': message,
            }
        if warning:
            res = {'warning': warning}
            return res

    qr_code_image = fields.Binary(string="QR Code:", attachment=True)
    
    # def _string_to_hex(self, value):
    #     if value:
    #         string = str(value)
    #         string_bytes = string.encode("UTF-8")
    #         encoded_hex_value = binascii.hexlify(string_bytes)
    #         hex_value = encoded_hex_value.decode("UTF-8")
    #         # print("This : "+value +"is Hex: "+ hex_value)
    #         return hex_value
    #
    # def is_arabic(self,name):
    #     str_utf8 = name.encode('utf-8')
    #     hex_str = str_utf8.hex()
    #     hex_lenth = len(hex_str)
    #     name_lenth = len(name)
    #     if hex_lenth/2 != name_lenth:
    #         return True
    #     else:
    #         return False
    #
    # def _get_hex(self, tag, length, value):
    #     if tag and length and value:
    #         # str(hex(length))
    #         hex_string = self._string_to_hex(value)
    #         str_seller = value.encode('utf-8')
    #         hex_str = str_seller.hex()
    #         if self.is_arabic(value):
    #             length = int(len(hex_str) / 2)
    #         else:
    #             length = len(value)
    #
    #         # print("LEN", length, " ", "LEN Hex", hex(length))
    #         conversion_table = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    #         hexadecimal = ''
    #         while (length > 0):
    #             remainder = length % 16
    #             hexadecimal = conversion_table[remainder] + hexadecimal
    #             length = length // 16
    #         # print(hexadecimal)
    #         if len(hexadecimal) == 1:
    #             hexadecimal = "0" + hexadecimal
    #         return tag + hexadecimal + hex_string
    #
    # def get_qr_code_data(self):
    #     if self.move_type in ('out_invoice', 'out_refund'):
    #         sellername = str(self.company_id.name)
    #         seller_vat_no = self.company_id.vat or ''
    #         if self.partner_id.company_type == 'company':
    #             customer_name = self.partner_id.name
    #             customer_vat = self.partner_id.vat
    #     else:
    #         sellername = str(self.partner_id.name)
    #         seller_vat_no = self.partner_id.vat
    #         customer_name = self.company_id.name
    #         customer_vat = self.company_id.vat
    #     seller_length = len(sellername)
    #     seller_hex = self._get_hex("01", "0c", sellername)
    #     vat_hex = self._get_hex("02", "0f", seller_vat_no)
    #     time_stamp = str(self.create_date)
    #     date_hex = self._get_hex("03", "14", time_stamp)
    #     total_with_vat_hex = self._get_hex("04", "0a", str(round(self.amount_total,2)))
    #     total_vat_hex = self._get_hex("05", "09", str(round(self.amount_tax,2)))
    #
    #     qr_hex = seller_hex+vat_hex+date_hex+total_with_vat_hex+total_vat_hex
    #     encoded_base64_bytes = base64.b64encode(bytes.fromhex(qr_hex)).decode()
    #
    #     return encoded_base64_bytes



    # qr_code_image = fields.Binary(string="QR Code", attachment=True, store=True)

    # @api.onchange('invoice_line_ids.product_id')
    # def generate_qr_code(self):
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=50,
    #         border=4,
    #     )
    #     qr.add_data(self.get_qr_code_data())
    #     qr.make(fit=True)
    #     img = qr.make_image()
    #     temp = BytesIO()
    #     img.save(temp, format="PNG")
    #     qr_image = base64.b64encode(temp.getvalue())
    #     self.qr_code_image = qr_image


    # def _generate_qr_code(self):
    #     system_parameter_url = request.env['ir.config_parameter'].get_param('web.base.url')
    #     system_parameter_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
    #     self.qr_code_image = self.create_qr_code(system_parameter_url)
