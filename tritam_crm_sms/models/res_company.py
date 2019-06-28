# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools,_
import re
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class Duoc_Sale_Order(models.Model):
    _inherit = "res.company"

    warehouse_phone = fields.Char('Warehouse Phone')


class Duoc_Res_Partner(models.Model):
    _inherit = "res.partner"

    sms = fields.Boolean(string=u'SMS', default=True,track_visibility='onchange')

