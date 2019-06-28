# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
import datetime
from odoo.exceptions import UserError


class tritam_country(models.Model):
    _inherit = 'res.country'

    x_country_code = fields.Char('Mã tỉnh VTP')
    ems_country_code = fields.Char('Mã tỉnh EMS')


class tritam_country(models.Model):
    _inherit = 'res.country.state'

    x_state_code = fields.Char('Mã tỉnh VTP')
    ems_state_code = fields.Char('Mã tỉnh EMS')
