# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.model
    def domain_source_customer(self):
        obj_source_customer = self.env['customer.source'].search([])
        arr_parent_id = []
        for rec in obj_source_customer:
            arr_parent_id.append(rec.parent_id.id)
        return [('id', 'not in', arr_parent_id),('x_active', '=', True)]

    source_customer = fields.Many2one('customer.source', 'Nguồn', domain=domain_source_customer)
    team_marketing = fields.Many2one('hr.department', related='source_customer.team_marketing', string='Team Marketing',
                                     readonly=True)




