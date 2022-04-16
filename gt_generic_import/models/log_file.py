
import time
from odoo import api, fields, models,_

class LogManagement(models.Model):
    _name = "log.management"
    _order='create_date desc'
    
    operation = fields.Selection([('po','Purchase Order'),('payment','Payment'),('so','Sale Order'),('inv','Invoice'),('picking','Picking'),('inventory','Inventory'),('bom','BOM'),('journal','Journal'),('bank','Bank Statement')],string="Operation")
    message = fields.Text(string='Message')


