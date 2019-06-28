# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools,_
import re
import datetime
from pytz import timezone
from dateutil.relativedelta import relativedelta


class Duoc_Crm_Lead(models.Model):
    _inherit = "crm.lead"

    @api.multi
    def pop_up_sms(self):
        self.ensure_one()
        return {
            'name': 'Message',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('tritam_crm_sms.pop_up_confirm_sms_crm_lead').id,
            'res_model': 'crm.lead.pop.up',
            'target': 'new',
        }

    class Duoc_Crm_Lead_Popup(models.TransientModel):
        _name = "crm.lead.pop.up"

        mail_template = fields.Many2one('mail.template', "SMS Template", domain=[('model_id.model', '=', 'crm.lead')])

        @api.multi
        def sent_sms(self):
            self.ensure_one()
            company_phone = self.env.user.company_id.phone or ""
            crm_lead = self.env['crm.lead'].browse(self._context.get('active_id'))
            content = re.sub(r'<.*?>', '', self.mail_template.body_html).replace('\n', '')
            content_cv = content.format(company_phone=company_phone,contact=crm_lead.partner_id.name,warehouse_phone=self.env.user.company_id.warehouse_phone or "",
                                        product=crm_lead.partner_id.x_product_id.name or "",
                                        category=crm_lead.partner_id.x_product_id.categ_id.name or "")
            if crm_lead.partner_id.phone and crm_lead.partner_id.sms:
                user_tz = self.env.user.tz or u'UTC'
                local_time = datetime.datetime.now(timezone(user_tz))
                utc_time = datetime.datetime.now(timezone('UTC'))
                if local_time.day > utc_time.day:
                    delay_hours_local = local_time.hour + 24 - utc_time.hour
                elif local_time.day < utc_time.day:
                    delay_hours_local = local_time.hour - (utc_time.hour + 24)
                else:
                    delay_hours_local = local_time.hour - utc_time.hour
                self.env['tritam.sms'].send_sms_api(crm_lead.partner_id.phone, content_cv)
                body_html = "<div><ul>" \
                        "<li>Gửi Sms</li>" \
                        "<li>Người gửi: {sale_man}</li>" \
                        "<li>Ngày gửi: {time}</li>" \
                        "<li>Hành động: gửi SMS</li>" \
                        "<li>Nội dung SMS: {note} </li>" \
                        "</ul></div>".format(sale_man=self.env.user.name,
                                             time=fields.datetime.now()-relativedelta(hours=delay_hours_local),note=content_cv)
                crm_lead.message_post(body_html)
                self.env['tritam.history.sms'].sudo().create({
                    'mail_template': self.mail_template.id,
                    'user_id': self.env.user.id,
                    'partner_id': crm_lead.partner_id.id,
                    'date': fields.datetime.now(),
                })
            return
