# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_system_link = fields.Char('Trang Báo cáo')
