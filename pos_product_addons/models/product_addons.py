# -*- coding: utf-8 -*-
import logging
import psycopg2
from odoo import models, fields, api, tools, _
_logger = logging.getLogger(__name__)


class PosProductAddonsConfig(models.Model):
    _inherit = 'product.template'

    has_addons = fields.Boolean('Has Add-ons')
    is_addons = fields.Boolean('Is Add-ons')
    addon_ids = fields.Many2many('product.product', string='Addons', domain="[('is_addons', '=', True)]")

    @api.onchange('is_addons', 'has_addons')
    def onchange_is_addons(self):
        """The function makes the corresponding product as 'Available In POS'
        if either 'is_addon' or 'has_addon' fields are true'"""
        if self.is_addons or self.has_addons:
            self.available_in_pos = True


class PosOrder(models.Model):
    """To write the product addons to backend """
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param dict order: dictionary representing the order.
        :param bool draft: Indicate that the pos_order is not validated yet.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns: id of created/updated pos.order
        :rtype: int
        """
        order = order['data']

        for lines in order.get('lines'):
            addons_total = 0
            for item in lines[2].get('addon_items'):
                addons_total += item.get('addon_price_with')

            lines[2]['price_unit'] = lines[2].get('price_unit') - addons_total
            lines[2]['price_subtotal'] = lines[2].get('price_subtotal') - addons_total
            lines[2]['price_subtotal_incl'] = lines[2].get('price_subtotal_incl') - addons_total

        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        addons = self.add_addons(order)  # adding the addons to the order

        pos_order = False

        if not existing_order:
            pos_order = self.create(self._order_fields(order))
            for rec in addons:
                pos_order.write({
                    'lines': [rec],
                })
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        pos_order = pos_order.with_company(pos_order.company_id)
        self = self.with_company(pos_order.company_id)
        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
            pos_order._create_order_picking()

        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order.action_pos_order_invoice()

        return pos_order.id

    def add_addons(self, order):
        """getting the addons line to write to pos order"""
        addon_list = []
        for rec in order.get('lines'):
            addon_list.append(rec[2])
        main = []
        final_adds = []
        for adds in addon_list:
            for items in adds['addon_items']:
                final_adds.append((0, 0, {
                    'qty': items['addon_count'],
                    'full_product_name': items['addon_name'],
                    'price_unit': items['addon_price_without'],
                    'product_id': items['addon_id'],
                    'product_uom_id': items['addon_uom'],
                    'price_subtotal': items['total_without'],
                    'price_subtotal_incl': items['total_with'],
                    'tax_ids': [[6, False, [items['tax']] if items.get('tax') else []]]

                }))
                main.append(final_adds)
        return final_adds
