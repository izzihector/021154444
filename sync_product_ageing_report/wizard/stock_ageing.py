# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

import xlwt
import base64
from io import BytesIO
from odoo import api, fields, models

class StockAgeingAnalysis(models.TransientModel):
    _name = "stock.ageing"
    _description = 'Stock Ageing Analysis'

    from_date = fields.Datetime(string="Date", required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, 
            default=lambda self: self.env.user.company_id.id)
    location_id = fields.Many2many('stock.location', string="Location")
    warehouse_ids = fields.Many2many('stock.warehouse', string="Warehouse")
    product_categ = fields.Many2many('product.category', string="Category")
    interval = fields.Integer(string="Interval(days)", default=30, required=True)
    data = fields.Char('Name',readonly=True)
    name = fields.Binary('Stock Ageing',readonly=True) 
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    filter_by = fields.Selection([('product', 'Product'), ('product_categ', 'Product Category')], required=True, default='product')
    product_ids = fields.Many2many('product.product', string="Product")

    def get_products(self):
        cr = self._cr
        if self.location_id and self.product_categ:
            cr.execute("select sq.id from stock_quant sq inner join product_product pp on(pp.id=sq.product_id) "
                       " inner join product_template pt on(pt.id=pp.product_tmpl_id and pt.categ_id in %s) "
                       "where sq.location_id in %s and sq.quantity > 0 and sq.in_date <=%s", (tuple(self.product_categ.ids),
                                                                     tuple(self.location_id.ids), self.from_date))
        elif self.location_id and self.product_ids:
            cr.execute("select sq.id from stock_quant sq where sq.location_id in %s and sq.quantity > 0 and sq.in_date <=%s "
                       "and product_id in %s",(tuple(self.location_id.ids), self.from_date, tuple(self.product_ids.ids)))
        elif self.location_id:
            cr.execute("select sq.id from stock_quant sq where sq.location_id in %s and sq.quantity > 0 and sq.in_date <=%s",
                       (tuple(self.location_id.ids), self.from_date))
        elif self.product_categ:
            cr.execute("select sq.id from stock_quant sq inner join product_product pp on(pp.id=sq.product_id) "
                       " inner join product_template pt on(pt.id=pp.product_tmpl_id and pt.categ_id in %s)"
                       "where sq.quantity > 0  and sq.in_date <=%s", (tuple(self.product_categ.ids), self.from_date))
        elif self.product_ids:
            cr.execute("select sq.id from stock_quant sq where sq.product_id in %s and sq.quantity > 0 and sq.in_date <=%s",
                       (tuple(self.product_ids.ids), self.from_date))
        else:
            cr.execute("select id from stock_quant where quantity > 0  and in_date <=%s and company_id=%s", (self.from_date, self.company_id.id))
        result = cr.fetchall()
        quant_ids = self.env['stock.quant'].browse([i[0] for i in result])
        if quant_ids and self.warehouse_ids:
            location_ids = self.warehouse_ids.mapped('view_location_id')
            quant_ids = self.env['stock.quant'].search([('location_id', 'child_of', location_ids.ids), ('id', 'in', quant_ids.ids)])
        products = {}
        product_list = []
        for quant_id in quant_ids:
            no_days = (self.from_date - quant_id.in_date).days
            t1 = 0
            t2 = self.interval
            if quant_id.product_id.id not in product_list:
                product_list.append(quant_id.product_id.id)
                qty_available = quant_id.product_id.with_context(company_owned=True, owner_id=False).qty_available
                temp = {
                    'product': quant_id.product_id.name,
                    'product_code': quant_id.product_id.default_code,
                    'total_qty': quant_id.quantity,
                    'total_value': quant_id.quantity * quant_id.product_id.standard_price,
                }
                qty = [0, 0, 0, 0, 0]
                val = [0, 0, 0, 0, 0]
                for j in range(0, 5):
                    if no_days >= 4 * self.interval:
                        qty[4] += quant_id.quantity
                        val[4] += quant_id.product_id.standard_price * quant_id.quantity
                        break
                    elif no_days in range(t1, t2):
                        qty[j] += quant_id.quantity
                        val[j] += quant_id.product_id.standard_price * quant_id.quantity
                        break
                    t1 = t2
                    t2 += self.interval
                temp['qty'] = qty
                temp['val'] = val
                products[quant_id.product_id.id] = temp
            elif quant_id.product_id.id in product_list:
                for j in range(0, 5):
                    if no_days >= 4 * self.interval:
                        products[quant_id.product_id.id]['qty'][4] += quant_id.quantity
                        products[quant_id.product_id.id]['val'][4] += quant_id.product_id.standard_price * quant_id.quantity
                        products[quant_id.product_id.id]['total_qty'] += quant_id.quantity
                        products[quant_id.product_id.id]['total_value'] += quant_id.quantity * quant_id.product_id.standard_price
                        break
                    elif no_days in range(t1, t2):
                        products[quant_id.product_id.id]['qty'][j] += quant_id.quantity
                        products[quant_id.product_id.id]['val'][j] += quant_id.product_id.standard_price * quant_id.quantity
                        products[quant_id.product_id.id]['total_qty'] += quant_id.quantity
                        products[quant_id.product_id.id]['total_value'] += quant_id.quantity * quant_id.product_id.standard_price
                        break
                    t1 = t2
                    t2 += self.interval
        return products

    def get_interval(self):
        return ['0-'+str(self.interval),
                    str(self.interval)+'-'+str(2*self.interval),
                    str(2*self.interval)+'-'+str(3*self.interval),
                    str(3*self.interval)+'-'+str(4*self.interval),
                    str(4*self.interval)+'+']

    def stock_ageing_pdf(self):
        return self.env.ref('sync_product_ageing_report.report_product_ageing').report_action(self)

    def stock_ageing_excel(self):
        fp = BytesIO()
        wb1 = xlwt.Workbook()
        header_content_style = xlwt.easyxf("font: name Times New Roman size 40 px , bold 1, height 280;align: vert centre, horiz centre")
        sub_header_style = xlwt.easyxf("font: name Times New Roman size 10 px, bold 1;align:horiz right")
        sub_header_style1 = xlwt.easyxf("font: name Times New Roman size 10 px, bold 1;align:horiz left")
        sub_header_style2 = xlwt.easyxf("font: name Times New Roman size 10 px, bold 1;align:horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Times New Roman size 10 px;align:horiz right")
        sub_header_content_style1 = xlwt.easyxf("font: name Times New Roman size 10 px;align:horiz left")
        sub_header_content_style2 = xlwt.easyxf("font: name Times New Roman size 10 px;align:horiz center")
        line_content_style = xlwt.easyxf("font: name Times New Roman;")
        ws1 = wb1.add_sheet('Stock Ageing')
        col_width = 256*15
        ws1.col(0).width = col_width
        ws1.col(1).width = col_width
        ws1.col(2).width = col_width
        ws1.col(3).width = col_width
        ws1.write_merge(1, 3, 0, 13, "Stock Ageing Report", header_content_style)
        ws1.write(5, 0, "Date", sub_header_style2)
        ws1.write(6, 0, str(self.from_date), sub_header_content_style2)
        ws1.write(5, 1, "Interval(Days)", sub_header_style2)
        ws1.write(6, 1, self.interval, sub_header_content_style2)
        if self.filter_by == "product":
            ws1.write_merge(5, 5, 2, 3, "Product", sub_header_style2)
            ws1.write_merge(6, 6, 2, 3, ', '.join(self.product_ids.mapped('name')), sub_header_content_style2)
        else:
            ws1.write_merge(5, 5, 2, 3, "Product Category", sub_header_style2)
            ws1.write_merge(6, 6, 2, 3, ', '.join(self.product_categ.mapped('display_name')), sub_header_content_style2)
        ws1.write_merge(5, 5, 4, 5, "Location", sub_header_style2)
        ws1.write_merge(6, 6, 4, 5, ', '.join(self.location_id.mapped('display_name')), sub_header_content_style2)
        ws1.write_merge(9, 10, 0, 0, "Product",sub_header_style1)
        ws1.write_merge(9, 10, 1, 1, "Internal Reference",sub_header_style1)
        ws1.write_merge(9, 10, 2, 2, "Total Qty",sub_header_style)
        ws1.write_merge(9, 10, 3, 3, "Total Value",sub_header_style)
        col = 4
        col1 = 5
        for rec in self.get_interval():
            ws1.write_merge(9, 9, col, col1, rec, sub_header_style2)
            ws1.write(10, col, "Qty", sub_header_style2)
            ws1.write(10, col1, "Value", sub_header_style2)
            col += 2
            col1 += 2
        row = 11
        data = self.get_products()
        for rec in data:
            ws1.write(row, 0, data[rec]['product'], sub_header_content_style1)
            ws1.write(row, 1, data[rec]['product_code'], sub_header_content_style1)
            ws1.write(row, 2, data[rec]['total_qty'], sub_header_content_style)
            ws1.write(row, 3, data[rec]['total_value'], sub_header_content_style)
            column1 = 4
            column2 = 5
            for qty in data[rec]['qty']:
                ws1.write(row, column1, qty, sub_header_content_style)
                column1 += 2
            for val in data[rec]['val']:
                ws1.write(row, column2, round(val, 4), sub_header_content_style)
                column2 += 2
            row += 1
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'name': out, 'data':'Stock Ageing.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.ageing',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }