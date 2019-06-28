# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools,_
import re
import datetime
from pytz import timezone
from dateutil.relativedelta import relativedelta


class Duoc_Sale_Order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        res = super(Duoc_Sale_Order, self).action_confirm()
        return {
            'name': 'Message',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('tritam_crm_sms.pop_up_confirm_sms_sale_order').id,
            'res_model': 'sale.order.pop.up',
            'target': 'new',
        }

    class Duoc_Crm_Lead_Popup(models.TransientModel):
        _name = "sale.order.pop.up"

        mail_template = fields.Many2one('mail.template', "SMS Template", domain=[('model_id.model', '=', 'sale.order')])

        @api.multi
        def sent_sms(self):
            self.ensure_one()
            sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
            lines =""
            for line in sale_order.order_line:
                qty = line.product_uom_qty or ""
                price_unit = line.price_unit or ""
                product = line.product_id.name or ""
                lines += "Số lượng: "+str(qty)+" Đơn Giá: "+str(price_unit)+" Sản Phẩm: "+str(product)+", "
            content = re.sub(r'<.*?>', '', self.mail_template.body_html).replace('\n', '')
            content_cv = content.format(lines=lines,amount_total=str(sale_order.amount_total),contact=sale_order.partner_id.name, address=sale_order.partner_id.contact_address or "",
                                        product=sale_order.partner_id.x_product_id.name or "",category=sale_order.partner_id.x_product_id.categ_id.name or "")
            if sale_order.partner_id.phone and sale_order.partner_id.sms:
                user_tz = self.env.user.tz or u'UTC'
                local_time = datetime.datetime.now(timezone(user_tz))
                utc_time = datetime.datetime.now(timezone('UTC'))
                if local_time.day > utc_time.day:
                    delay_hours_local = local_time.hour + 24 - utc_time.hour
                elif local_time.day < utc_time.day:
                    delay_hours_local = local_time.hour - (utc_time.hour + 24)
                else:
                    delay_hours_local = local_time.hour - utc_time.hour
                self.env['tritam.sms'].send_sms_api(sale_order.partner_id.phone, content_cv)
                body_html = "<div><ul>" \
                        "<li>Gửi Sms</li>" \
                        "<li>Người gửi: {sale_man}</li>" \
                        "<li>Ngày gửi: {time}</li>" \
                        "<li>Hành động: gửi SMS</li>" \
                        "<li>Nội dung SMS: {note} </li>" \
                        "</ul></div>".format(sale_man=self.env.user.name,
                                             time=fields.datetime.now()-relativedelta(hours=delay_hours_local),note=content_cv)
                sale_order.message_post(body_html)
                self.env['tritam.history.sms'].sudo().create({
                    'mail_template': self.mail_template.id,
                    'user_id': self.env.user.id,
                    'partner_id': sale_order.partner_id.id,
                    'date': fields.datetime.now(),
                })
            return
