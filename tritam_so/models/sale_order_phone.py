# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.base_phone import fields

from odoo.exceptions import AccessDenied, UserError
from odoo.exceptions import ValidationError


class tritam_sale_order(models.Model):
    _inherit = 'sale.order'

    phone = fields.Phone(string='Phone')
    mobile = fields.Phone(string='Mobile')

    @api.onchange('partner_id')
    def onchange_phone_mobile(self):
        values = {}
        if self.partner_id:
            values['phone'] = self.partner_id.phone
        if self.partner_id:
            values['mobile'] = self.partner_id.mobile
        self.update(values)

    @api.constrains('mobile')
    def _verify_mobile(self):
        for r in self:
            if r.mobile != r.partner_id.mobile:
                raise ValidationError('Không khớp mobile')

    @api.constrains('phone')
    def _verify_phone(self):
        for r in self:
            if r.phone != r.partner_id.phone:
                raise ValidationError('Không khớp phone')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # phone = fields.Phone(string='Phone', related='partner_id.phone')
    # mobile = fields.Phone(string='mobile', related='partner_id.mobile')


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # phone = fields.Phone(string='Phone', related='partner_id.phone')
    # mobile = fields.Phone(string='mobile', related='partner_id.mobile')



