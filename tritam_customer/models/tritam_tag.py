# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
import datetime
from odoo.exceptions import UserError


class tritam_tag(models.Model):
    _inherit = 'res.partner.category'

    x_active = fields.Boolean(string ='Hiện đang sử dụng', default=True)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self._context.get('partner_search'):
            domain.append(['x_active', '=',True ])
        return super(tritam_tag, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
                                                       order=order)

    @api.multi
    def name_get(self):
        if self._context.get('partner_search') and self._context.get('flag_create') is False :
            result = []
            for r in self:
                if r.x_active == True:
                    result.append((r.id,r.name))
            return result
        return super(tritam_tag, self).name_get()

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     return super(tritam_tag, self).name_search(name='', args=None, operator='ilike', limit=100)