# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from datetime import timedelta
import datetime
from odoo.exceptions import AccessDenied, UserError
import logging


class Duocphanbo_inherit(models.Model):
    _inherit = 'res.automatic'

    # @api.model
    # def action_hotline(self):
    #     return super(Duocphanbo_inherit, self).action_hotline()

    @api.model
    def action_in(self):
        return super(Duocphanbo_inherit, self).action_in()

    # @api.model
    # def action_18h(self):
    #     return super(Duocphanbo_inherit, self).action_18h()
    #
    # @api.model
    # def action_renew_rp(self):
    #     return super(Duocphanbo_inherit, self).action_renew_rp()
    #
    # @api.model
    # def action_to_sign(self):
    #     return super(Duocphanbo_inherit, self).action_to_sign()
    #
    # @api.model
    # def action_to_sp(self):
    #     return super(Duocphanbo_inherit, self).action_to_sp()
    #
    # @api.model
    # def action_to_support_need_sp(self):
    #     return super(Duocphanbo_inherit, self).action_to_support_need_sp()
    #
    # @api.model
    # def action_to_sign_recall(self):
    #     return super(Duocphanbo_inherit, self).action_to_sign_recall()