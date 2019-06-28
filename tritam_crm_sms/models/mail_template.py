# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools,_
import re
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class MailTemplate(models.Model):
    _inherit = "mail.template"

    group_ids = fields.Many2many('res.groups', 'mail_template_res_groups_rel', 'mail_id', 'group_id', string='Group User')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):

        res = super(MailTemplate, self).name_search(name=name, args=args, operator=operator, limit=limit)
        if self._context.get('show_group'):
            list = self.search([('group_ids', 'in', self.env.user.groups_id.ids)]).ids
            nonelist = self.search([('group_ids', '=', False)]).ids
            list += nonelist
            args += [['id', 'in', list]]
            res = super(MailTemplate, self).name_search(name=name, args=args, operator=operator, limit=limit)
        return res