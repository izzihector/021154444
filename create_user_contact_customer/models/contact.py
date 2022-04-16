# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Contact(models.Model):
    _inherit = 'res.partner'

    custom_is_add_user = fields.Boolean(
        'Create Portal User?',
        copy=True,
    )
    custom_is_add_child_user = fields.Boolean(
        'Create Portal User Contacts?',
        copy=True,
    )

    def custom_action_grant_access(self):
        if self._context.get('active_ids'):
            partner_ids = self._context.get('active_ids')
        else:
            if self.custom_is_add_child_user:
                partner_ids = self.child_ids.ids + self.ids
            else:
                partner_ids = self.ids
        return self._custom_action_grant_access(partner_ids)

    def _custom_action_grant_access(self, partner_ids):
        active_ids = partner_ids
        users_dict = self.env['res.users'].search_read([('partner_id', 'in', active_ids)], fields=['id', 'name', 'partner_id'])
        partner_dict = dict([i.get('partner_id') for i in users_dict if i.get('partner_id')])
        existing_partner_ids = list(partner_dict.keys())
        active_partner_ids = []
        if active_ids and existing_partner_ids:
            active_partner_ids = list(set(active_ids)^set(existing_partner_ids))
        else:
            active_partner_ids = active_ids
        wizard = self.env['portal.wizard'].create({'partner_ids': [(6, 0, active_partner_ids)]})
        for user in wizard.user_ids:
            user.with_context(custom_skip_open_modal=True).action_grant_access()
        
        if existing_partner_ids:
            existing_partners = ' | '.join(partner_dict.values())
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Allready linked.'),
                    'message': _('%s are allready linked.' %(existing_partners)),
                    'type': 'warning',
                    'sticky': True,
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
