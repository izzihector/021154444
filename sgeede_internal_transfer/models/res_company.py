# -*- coding: utf-8 -*-
import json
import time
import logging
import odoo.addons.decimal_precision as dp
from datetime import date, datetime
from dateutil import relativedelta
from odoo import fields, models
from odoo.tools import float_compare
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

class res_company(models.Model):
    _inherit = "res.company"

    transit_location_id = fields.Many2one('stock.location', 'Transit Location')