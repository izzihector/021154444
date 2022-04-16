# Copyright 2018 FOREST AND BIOMASS ROMANIA SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.osv import expression
from odoo import fields, models, api

class AccountSubGroup(models.Model):
    _name = "account.subgroup"
    _description = 'Account Sub-Group'
    _parent_store = True
    _order = 'code_prefix'

    parent_id = fields.Many2one('account.subgroup', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    name = fields.Char(required=True)
    code_prefix = fields.Char()

    def name_get(self):
        result = []
        for group in self:
            name = group.name
            if group.code_prefix:
                name = group.code_prefix + ' ' + name
            result.append((group.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        criteria_operator = ['|'] if operator not in expression.NEGATIVE_TERM_OPERATORS else ['&', '!']
        domain = criteria_operator + [('code_prefix', '=ilike', name + '%'), ('name', operator, name)]
        group_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(group_ids).name_get()

class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    @api.depends('tag_ids')
    def _get_tag_search_string(self):
        for rec in self:
            name_search_string = rec.name
            for tag in rec.tag_ids:
                name_search_string += '|' + tag.name
            rec.tag_ids_name = name_search_string
        return name_search_string

    
    subgroup_id = fields.Many2one('account.subgroup')
    tag_ids_name = fields.Char(compute="_get_tag_search_string",string="Tags name",store="True")    
    
    
    