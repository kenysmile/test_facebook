# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools,_



class Duoc_Delivery_Carrier(models.Model):
    _name = "tritam.history.sms"

    mail_template = fields.Many2one('mail.template', "Tên Kịch Bản")
    user_id = fields.Many2one('res.users', string='Người Xác Nhận Gửi')
    partner_id = fields.Many2one('res.partner', string="Khách Hàng")
    date = fields.Datetime('Ngày gửi')

