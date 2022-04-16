from odoo import fields, models, api
import uuid
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_set_quantities_to_reservation(self):
        i = 1100
        for move in self:
            for move_line in move.move_line_ids:
                if move.has_tracking != 'none':
                    # lot_name = uuid.uuid4()
                    if not move_line.lot_name:
                        date_time = datetime.now().strftime('%Y/%m/%d/%H/%M/%S')
                        lot_name = str(self.erp_po_code) + "/" + date_time + "/" + str(self.id)+str(i)
                        move_line.update({'lot_name': lot_name})
                        i = i + 1

        return super(StockPicking, self).action_set_quantities_to_reservation()