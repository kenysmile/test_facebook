# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools,_
import calendar
from datetime import timedelta, date
import datetime
import re
from threading import Timer, Thread
#import imp
import sys
#reload(sys)
#sys.setdefaultencoding("utf8")
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from pytz import timezone
from dateutil.relativedelta import relativedelta


class Duoc_Delivery_Carrier(models.Model):
    _inherit = "delivery.carrier"

    type_method = fields.Selection([
        (1, 'Ship ngoài'),
        (2, 'Hãng vận chuyển'),
    ], string='Loại vận chuyển', default= 1)
    mail_template = fields.Many2one('mail.template', "SMS Template", domain=[('model_id.model', '=', 'stock.picking')])
    mail_template_do_out = fields.Many2one('mail.template', "SMS Template DO OUT", domain=[('model_id.model', '=', 'stock.picking')])
    link_shipping = fields.Char(string="Link tra cứu MVĐ")


class Duoc_Stock_Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_new_transfer(self):

        # so = self.env['sale.order'].browse(self.group_id.procurement_ids[0].sale_line_id.order_id.id) \
        #      or self.env['sale.order'].search([('name','=',self.group_id.name)])
        if self.group_id.procurement_ids:
            so = self.env['sale.order'].browse(self.group_id.procurement_ids[0].sale_line_id.order_id.id)
        else:
            so = self.env['sale.order'].search([('name', '=', self.group_id.name)])
        user_tz = self.env.user.tz or u'UTC'
        local_time = datetime.datetime.now(timezone(user_tz))
        utc_time = datetime.datetime.now(timezone('UTC'))
        if local_time.day > utc_time.day:
            delay_hours_local = local_time.hour + 24 - utc_time.hour
        elif local_time.day < utc_time.day:
            delay_hours_local = local_time.hour - (utc_time.hour + 24)
        else:
            delay_hours_local = local_time.hour - utc_time.hour
        if self.name.find('PICK') != -1:
            if so.carrier_id:
                if not so.carrier_id.mail_template:
                    raise UserError(_("Phương án giao hàng của %s chưa có SMS Template " % (so.name)))
                lines = ""
                for line in so.order_line:
                    qty = line.product_uom_qty or ""
                    price_unit = line.price_unit or ""
                    product = line.product_id.name or ""
                    lines += "Số lượng: " + str(qty) + " Đơn Giá: " + str(price_unit) + " Sản Phẩm: " + str(
                        product) + ", "
                content = re.sub(r'<.*?>', '', so.carrier_id.mail_template.body_html).replace('\n', '')
                content_cv = content.format(lines=lines, amount_total=str(so.amount_total),
                                            contact=so.partner_id.name,
                                            address=so.partner_id.contact_address or "",
                                            sale_order=so.name,link_mvd=so.carrier_id.link_shipping or "",company_phone=self.env.user.company_id.phone or "",
                                            product=so.partner_id.x_product_id.name or "",
                                            category=so.partner_id.x_product_id.categ_id.name or "")
                if so.carrier_id.type_method == 1:
                    if so.partner_id.phone and so.partner_id.sms:
                        self.env['tritam.sms'].send_sms_api(so.partner_id.phone, content_cv)
                        body_html = "<div><ul>" \
                                    "<li>Gửi Sms</li>" \
                                    "<li>Người gửi: {sale_man}</li>" \
                                    "<li>Ngày gửi: {time}</li>" \
                                    "<li>Hành động: gửi SMS</li>" \
                                    "<li>Nội dung SMS: {note} </li>" \
                                    "</ul></div>".format(sale_man=self.env.user.name,
                                                         time=fields.datetime.now()-relativedelta(hours=delay_hours_local), note=content_cv)
                        self.message_post(body_html)
                        self.env['tritam.history.sms'].sudo().create({
                            'mail_template': so.carrier_id.mail_template.id,
                            'user_id': self.env.user.id,
                            'partner_id': so.partner_id.id,
                            'date': fields.datetime.now(),
                        })
                elif so.carrier_id.type_method == 2:

                    now = datetime.datetime.now()-relativedelta(hours=delay_hours_local)
                    run_at = (now + timedelta(days=1))
                    giventime = run_at.replace(hour=8, minute=00, second=0, microsecond=0)
                    _logger.info(
                        "--------------before-------------" + str(now)+"------------------------------------------")
                    _logger.info(
                        "--------------before-------------" + str(giventime)+"------------------------------------------")
                    if so.partner_id.phone and so.partner_id.sms:
                        self.env['tritam.sms'].send_sms_api_delay(so.partner_id.phone, content_cv,str(giventime))
                        body_html = "<div><ul>" \
                                    "<li>Gửi Sms</li>" \
                                    "<li>Người gửi: {sale_man}</li>" \
                                    "<li>Ngày gửi: {time}</li>" \
                                    "<li>Hành động: gửi SMS</li>" \
                                    "<li>Nội dung SMS: {note} </li>" \
                                    "</ul></div>".format(sale_man=self.env.user.name,
                                                         time=giventime, note=content_cv)
                        self.message_post(body_html)
                        self.env['tritam.history.sms'].sudo().create({
                            'mail_template': so.carrier_id.mail_template.id,
                            'user_id': self.env.user.id,
                            'partner_id': so.partner_id.id,
                            'date': str(giventime+relativedelta(hours=delay_hours_local)),
                        })
                else :
                    raise UserError(_("Phương án giao hàng của %s chưa có loại vận chuyển" % (so.name)))
            else:
                raise UserError(_("%s chưa có phương án giao hàng"%(so.name)))
        if self.name.find('OUT') != -1:
            if so.carrier_id:
                if not so.carrier_id.mail_template_do_out:
                    raise UserError(_("Phương án giao hàng của %s chưa có SMS Template " % (so.name)))
                content = re.sub(r'<.*?>', '', so.carrier_id.mail_template_do_out.body_html).replace('\n', '')
                content_cv = content.format(contact=so.partner_id.name,product = so.partner_id.x_product_id.name or "",
                                            category=so.partner_id.x_product_id.categ_id.name or "")
                if so.partner_id.phone and so.partner_id.sms:
                    self.env['tritam.sms'].send_sms_api(so.partner_id.phone, content_cv)
                    body_html = "<div><ul>" \
                                "<li>Gửi Sms</li>" \
                                "<li>Người gửi: {sale_man}</li>" \
                                "<li>Ngày gửi: {time}</li>" \
                                "<li>Hành động: gửi SMS</li>" \
                                "<li>Nội dung SMS: {note} </li>" \
                                "</ul></div>".format(sale_man=self.env.user.name,
                                                     time=fields.datetime.now()-relativedelta(hours=delay_hours_local), note=content_cv)
                    self.message_post(body_html)
                    self.env['tritam.history.sms'].sudo().create({
                        'mail_template': so.carrier_id.mail_template_do_out.id,
                        'user_id': self.env.user.id,
                        'partner_id': so.partner_id.id,
                        'date': fields.datetime.now(),
                    })
            else:
                raise UserError(_("%s chưa có phương án giao hàng"%(so.name)))
        res = super(Duoc_Stock_Picking, self).do_new_transfer()
        return res

