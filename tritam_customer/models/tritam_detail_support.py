# -*- coding: utf-8 -*-
from odoo import models, fields, api
import time
from datetime import datetime, timedelta
from dateutil import relativedelta
import logging


class tritam_detail_support(models.Model):
    _name = 'tritam_detail_support'

    product_id = fields.Many2one('product.product', string='Product',required=True)
    order_id = fields.Many2one('sale.order', 'Sale Order')
    parent_id = fields.Many2one('res.partner')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    @api.multi
    def schedule_date(self):
        today = datetime.strptime(fields.Date.today(), '%Y-%m-%d')
        obj_self = self.search([])
        for rec in obj_self :
            end_date = datetime.strptime(rec.end_date, '%Y-%m-%d')
            if (today - end_date).days == 0 :
                rec.parent_id.write({'to_sign':'yes'})
