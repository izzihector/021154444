from odoo import fields, models, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', required=True, related="picking_type_id.warehouse_id",
        domain="[('company_id', '=', company_id)]")

    limited_partners_loading = fields.Boolean('Limited Partners Loading', default=True,
                                              help="By default, 100 partners are loaded.\n"
                                                   "When the session is open, we keep on loading all remaining partners in the background.\n"
                                                   "In the meantime, you can use the 'Load Customers' button to load partners from database.")
    partner_load_background = fields.Boolean(default=True)

    def get_limited_partners_loading(self):
        self.env.cr.execute("""
                    WITH pm AS
                    (
                             SELECT   partner_id,
                                      Count(partner_id) order_count
                             FROM     pos_order
                             GROUP BY partner_id)
                    SELECT    id
                    FROM      res_partner AS partner
                    LEFT JOIN pm
                    ON        (
                                        partner.id = pm.partner_id)
                    where warehouse_id=%s and active='1' 
                    ORDER BY  COALESCE(pm.order_count, 0) DESC,
                              NAME limit %s;
                """, [str(self.warehouse_id.id), str(self.limited_partners_amount)])

        result = self.env.cr.fetchall()
        print("result::", result)
        return result