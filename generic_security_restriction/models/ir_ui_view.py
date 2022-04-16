import json
import logging

from odoo import models,fields

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    def _postprocess_tag_field(self, node, name_manager, node_info):

        result = super(IrUiView, self)._postprocess_tag_field(
            node, name_manager, node_info)

        field_security = self.env['ir.model']._get(
            name_manager.model._name
        ).mapped('field_security_ids').search(
            [('field_name', '=', node.get('name'))]
        )
        if not self.env.user.groups_id & field_security.group_ids:
            return result

        if field_security.set_invisible:
            node.set('invisible', '1')
            node_info['modifiers']['invisible'] = field_security.set_invisible
        if field_security.set_readonly:
            node.set('readonly', '1')
            node_info['modifiers']['readonly'] = field_security.set_readonly
        if (field_security.field_type == 'many2one' and
                field_security.rewrite_options):
            options = {
                'no_open': field_security.set_no_open,
                'no_create': field_security.set_no_create,
                'no_quick_create':
                    field_security.set_no_quick_create,
                'no_create_edit': field_security.set_no_create_edit
            }
            node.set('options', json.dumps(options))
        return result

    def _postprocess_tag_button(self, node, name_manager, node_info):

        postprocessor = getattr(
            super(IrUiView, self), '_postprocess_tag_button', False)
        if postprocessor:
            super(IrUiView, self)._postprocess_tag_button(
                node, name_manager, node_info)

        fields_security = self.env['ir.model']._get(
            name_manager.model._name
        ).mapped('field_security_ids')

        fields_hide_stat_button = fields_security.search(
            [
                ('field_name', 'in',
                 [i.get('name') for i in node.iter(tag='field')]),
                ('hide_stat_button', '=', True)
            ]
        )

        if not self.env.user.groups_id & fields_hide_stat_button.group_ids:
            return None

        if fields_hide_stat_button:
            node.set('invisible', '1')
            node_info['modifiers']['invisible'] = bool(fields_hide_stat_button)

        return None
