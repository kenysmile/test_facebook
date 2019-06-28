# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    usage_time = fields.Integer(string="Thời gian sử dụng")
    recurring_date = fields.Integer(string='Thời gian đến hạn tái ký')

    @api.multi
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.read(['name'])
        return [(template.id, '%s' % (template.name)) for template in self]

class tritam_product_price_list(models.Model):
    _inherit = 'product.pricelist'

    date_start = fields.Date('Start Date', help="Starting date for the pricelist item validation")
    date_end = fields.Date('End Date', help="Ending valid for the pricelist item validation")
    date_creat = fields.Datetime('Creat Date', default=fields.Datetime.now, readonly=True)
    x_user_id = fields.Many2one('res.users',default=lambda self: self.env.uid,readonly=True )


class tritam_product_price_list_items(models.Model):
    _inherit = 'product.pricelist.item'

    old_price = fields.Float('Old Price',compute='_compute_old_price')
    date_start = fields.Date('Start Date', help="Starting date for the pricelist item validation",compute='compute_date_price_list')
    date_end = fields.Date('End Date', help="Ending valid for the pricelist item validation",compute='compute_date_price_list')
    # pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', index=True, ondelete='cascade',default=_get_default_pricelist_id)

    @api.one
    @api.depends('pricelist_id')
    def compute_date_price_list(self):
        self.date_start = self.pricelist_id.date_start
        self.date_end = self.pricelist_id.date_end

    @api.one
    @api.depends('product_tmpl_id')
    def _compute_old_price(self):
        self.old_price = self.product_tmpl_id.list_price





