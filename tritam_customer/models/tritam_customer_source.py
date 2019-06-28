# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging


class tritam_customer_source(models.Model):
    _name = 'customer.source'
    _rec_name = 'name'

    name = fields.Char(string=u'Tên')
    parent_id = fields.Many2one('customer.source',string='Nguồn cha')
    team_marketing = fields.Many2one('hr.department',string='Team Marketing',required=True)
    x_user_id = fields.Many2one('res.users', string='Nhân Viên',required=True)
    x_product_id = fields.Many2one('product.product',string='Product',required=True)
    x_active = fields.Boolean('Active', default=True)
    # number_customer = fields.Integer(compute="associate_count")
    utm_id = fields.Many2one('utm.source', string='Kênh marketing')

    @api.multi
    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    # @api.multi
    # def associate_count(self):
    #     for rec in self:
    #         ids = self.search([('id', 'child_of', rec.id)]).ids
    #         rec.number_customer = self.env['res.partner'].search_count([('source_customer', 'in', ids)])

    @api.multi
    def x_toggle_active(self):
        for record in self:
            record.x_active = not record.x_active