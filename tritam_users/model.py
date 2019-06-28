# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DuocUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        if vals.get('code_user', '/') == False:
            vals['code_user'] = self.env['ir.sequence'].get('res.user.code')
            if vals['code_user'] != False:
                new_id = super(DuocUsers, self).create(vals)
                return new_id
        else:
            return super(DuocUsers, self).create(vals)

    def _default_category(self):
        return self.env['res.partner.category'].browse(self._context.get('category_id'))

    category_id = fields.Many2many('res.partner.category', relation='rel_user_category' ,column1='user_id',
                                   column2='category_id', string='Tags', default=_default_category, copy=False)

    code_user = fields.Char(string='Code', help='Mã nhân viên')
    new_contact = fields.Integer('Contact mới/ngày')
    re_contact = fields.Integer('Contact tái sử dụng/ngày')
    re_sign = fields.Integer('Contact tái kí/ngày')
    re_sp = fields.Integer('Contact CSKH/ngày')

    # ratio = fields.Float(digits=(12, 1), string='Tỉ lệ')


