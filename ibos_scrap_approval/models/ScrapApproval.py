# -*- coding: utf-8 -*-from odoo import api, fields, models
from odoo import api, fields, models, _

from datetime import datetime, timedelta
from odoo.modules.module import get_module_resource


class StockApproval(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherit = "stock.scrap"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_submit', 'To Submit'), ('submitted', 'Submitted'), ('approve', 'Approved'),
        ('refuse', 'Refused'), ('store', 'Draft'),('done', 'Done')],
        string='Status', default="to_submit", readonly=True, tracking=True)
    date_done = fields.Datetime(readonly=True)

    def action_submit_manager(self):
        self.state = 'submitted'
        if self.state == 'submitted':
            self.message_post()
            self.date_done = datetime.now()

    def action_approve(self):
        self.state = 'approve'
        self.message_post()
        if self.state == 'approve':
            user_obj = self.env['res.users'].search([])
            for user_login in user_obj:
                current_login = self.env.user
                if user_login == current_login:
                    print(user_login.name)
                    self.approved_by = user_login.name
                    self.date_done = datetime.now()
        return self

    approved_by = fields.Char(string="Approve By")

    def action_refuse(self):
        self.state = 'refuse'
        if self.state == 'refuse':
            user_obj = self.env['res.users'].search([])
            for user_login in user_obj:
                current_login = self.env.user
                if user_login == current_login:
                    print(user_login.name)
                    self.refuse_by = user_login.name
                    self.date_done = datetime.now()
                    self.message_post()
            return self

    refuse_by = fields.Char(string="Refused By")

    def action_draft(self):
        self.state = "store"
        self.message_post()
        if self.state == "store":
            self.refuse_reason = ""
            self.refuse_by = ""
            self.date_done = ""
            self.approved_by = ""
            self.date_done = datetime.now()

    refuse_reason = fields.Char(string="Refuse Reason", readonly=True)

    def action_validate(self):
        return self.do_scrap()


def get_module_icon(module):
    iconpath = ['static', 'description', 'icon.png']
    if get_module_resource(module, *iconpath):
        return ('/' + module + '/') + '/'.join(iconpath)
    return '/base/' + '/'.join(iconpath)
