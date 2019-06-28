# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools,_
from datetime import datetime, timedelta
from odoo.exceptions import UserError


# Cap Nhat Trang Thai chuyen dich kho (daft)
class Update_Invoice_Out(models.Model):
    _inherit = "stock.picking"


# cap nhat trang thai hoa don
# class Update_Invoice(models.Model):
#     _inherit = "account.invoice"
#
#     @api.multi
#     def schedule_update_invoice(self):
#         self.env.cr.execute(
#             """DELETE FROM account_invoice WHERE origin = '%s'""" % ('SO24129'))
#         self.env.cr.execute(
#             """DELETE FROM account_invoice WHERE origin = '%s'""" % ('INV/2018/6043'))
#         print "ok"


# cap nhat trang thai don hang
class Update_Sale_Order(models.Model):
    # _inherit = "account.invoice"
    _inherit = "sale.order"


class Duoc_Crm_Lead(models.Model):

    _inherit = "crm.lead"

    @api.model
    def get_date(self):
        import datetime
        return datetime.date.today()

    date_create = fields.Date(default=get_date)

    # @api.multi
    # def icron_change_lost_reason(self):
    #
    #     obj_crm_lead = self.search([('active', '=', False),('probability', '=', 0), ('lost_reason', 'in', [5])])
    #     reason = self.env['crm.lost.reason'].search([('type_state', '=', 2)],
    #                                                 limit=1)
    #     # print len(obj_crm_lead)
    #     list_crm_lost = []
    #     for item in obj_crm_lead:
    #         list_crm_lost.append(item.id)
    #     if reason:
    #         reason_id = reason.id
    #         print reason_id
    #     if list_crm_lost:
    #         self.env.cr.execute(
    #             """UPDATE crm_lead SET lost_reason = %s WHERE id in %s""" % (
    #                 reason_id, tuple(list_crm_lost)))
        # print "ok"

    # @api.multi
    # def icron_change_stage_and_probability(self):
    #     obj_crm_lead = self.search([('active', '=', True)])
    #     # print([item.stage_id.name for item in obj_crm_lead if item.stage_id.name == u'Cần chăm sóc hôm nay'])
    #
    #     list_ticket_apply = [item.id for item in obj_crm_lead if
    #                           item.stage_id.name.startswith(u'Đã hết hạn chăm sóc')]
    #     if list_ticket_apply:
    #         self.env.cr.execute(
    #             """UPDATE crm_lead SET probability = %s WHERE id in %s""" % (
    #                 50, tuple(list_ticket_apply)))

    # @api.multi
    @api.model
    def schedule_reject_ticket(self):
        today = datetime.strptime(fields.Datetime.now(),tools.DEFAULT_SERVER_DATETIME_FORMAT)
        obj_crm_stage = self.env['crm.stage'].search([('probability','in', [100])])
        obj_crm_lead = self.search([('active','=',True),('stage_id.id','not in',obj_crm_stage.ids),('type_contact','not in',['sp'])])
        reason = self.env['crm.lost.reason'].search([('type_state', '=', 1)], limit=1)
        day_new_contact = self.env['res.automatic.share.settings'].sudo().search([])[0].conf_new_contact
        day_re_use = self.env['res.automatic.share.settings'].sudo().search([])[0].conf_re_use
        number_re_sign = self.env['res.automatic.share.settings'].sudo().search([])[0].conf_re_sign

        list_ticket_apply = []
        list_res_partner = []
        if reason:
            id_reason = reason.id
        else:
            raise UserError(_("Chưa cài đặt loại cho một lý do là Quá Hạn"))
        for rec in obj_crm_lead:
            number_day = day_re_use if rec.type_contact == "reuse" else number_re_sign if rec.type_contact == "contract" else day_new_contact
            create_date = datetime.strptime(rec.create_date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            real_date = create_date + timedelta(days=number_day)
            if (real_date - today ).days < 0:
                list_ticket_apply.append(rec.id)
                rec.action_set_lost()
                if len(rec.partner_id.ids) > 0:
                    list_res_partner.append(rec.partner_id.id)
        if(list_ticket_apply):
            self.env.cr.execute("""UPDATE crm_lead SET lost_reason = %s WHERE id in %s""" % (id_reason, tuple(list_ticket_apply)))
        if(list_res_partner):
            self.env.cr.execute("""UPDATE res_partner SET reuse = '%s' WHERE id in %s""" % ('yes', tuple(list_res_partner)))


    # reject cts Moi co trang thai KNM ve Tai Su Dung sau 18:00:00
    @api.multi
    @api.model
    def schedule_reject_ticket_new_to_reuse(self):
        today = datetime.strptime(fields.Datetime.now(),
                                  tools.DEFAULT_SERVER_DATETIME_FORMAT)
        obj_crm_stage = self.env['crm.stage'].search(
            [('probability', 'in', [70])])
        obj_crm_lead = self.env['crm.lead'].sudo().search([
            ('active', '=', True),
            ('stage_id.id', 'in', obj_crm_stage.ids),
            ('type_contact', 'in', ['new'])])
        # print obj_crm_lead
        reason = self.env['crm.lost.reason'].search([('type_state', '=', 1)],
                                                    limit=1)
        day_new_contact = \
        self.env['res.automatic.share.settings'].sudo().search([])[
            0].conf_new_cts_knm

        list_ticket_apply = []
        list_res_partner = []
        if reason:
            id_reason = reason.id
        else:
            raise UserError(_("Chưa cài đặt loại cho một lý do là Quá Hạn"))
        for rec in obj_crm_lead:
            # print "trang thai", rec.stage_id.name, "Kieu", rec.type_contact
            number_day = day_new_contact
            if rec.stage_id.name.startswith(u"Cần gọi lại"):
                # create_date = datetime.strptime(rec.create_date,
                #                                 tools.DEFAULT_SERVER_DATETIME_FORMAT)
                writes_date = datetime.strptime(rec.write_date,
                                                tools.DEFAULT_SERVER_DATETIME_FORMAT)
                real_date = writes_date + timedelta(days=number_day)
                # print "hieu", (real_date - today ).days
                if (real_date - today).days == 0:
                    list_ticket_apply.append(rec.id)
                    rec.action_set_lost()
                    if len(rec.partner_id.ids) > 0:
                        list_res_partner.append(rec.partner_id.id)
        # print "ticket list", list_ticket_apply
        # print "partner list", list_res_partner
        if (list_ticket_apply):
            self.env.cr.execute(
                """UPDATE crm_lead SET lost_reason = %s WHERE id in %s""" % (
                id_reason, tuple(list_ticket_apply)))
        if (list_res_partner):
            self.env.cr.execute(
                """UPDATE res_partner SET reuse = '%s' WHERE id in %s""" % (
                'yes', tuple(list_res_partner)))


    # Loc Cac Ticket Trung Nhau Giu lai ticket co date update gan nhat
    # @api.multi
    # def reject_ticket_repeat(self):
    #     today = datetime.strptime(fields.Datetime.now(),
    #                               tools.DEFAULT_SERVER_DATETIME_FORMAT)
    #     cus_phone_obj = self.env['res.partner'].search([("active","=", True), ('phone', '!=', False)], limit=250000)
    #
    #     cus_phone = [x.phone for x in cus_phone_obj]
    #     # print cus_phone
    #     for p in cus_phone:
    #         p = p.strip()
    #         # print p
    #         obj_crm_lead = self.env['crm.lead'].search([('active', '=', True), ('phone', '=', p)])
    #         # print len(obj_crm_lead)
    #         date_update = [datetime.strptime(c.write_date,
    #                                          tools.DEFAULT_SERVER_DATETIME_FORMAT)
    #                        for c in obj_crm_lead]
    #         lst_hieu = []
    #         if len(obj_crm_lead) > 1:
    #             for x in date_update:
    #                 hieu = (today - x).days
    #                 lst_hieu.append(hieu)
    #             min_hieu = min(lst_hieu)
    #             for item in obj_crm_lead:
    #                 date_up = datetime.strptime(item.write_date,
    #                                             tools.DEFAULT_SERVER_DATETIME_FORMAT)
    #                 if (today - date_up).days > min_hieu:
    #                     self.env.cr.execute(
    #                         "UPDATE crm_lead SET active='%s' WHERE id=%s" % (
    #                         False, item.id))

    # Chon ngay Phan Bo de thay doi ngay tao
    # @api.multi
    # def Change_create_on2(self):
    #     cus_phone_obj = self.env['res.partner'].search(
    #         [("active", "=", True), ('phone', '!=', False),
    #          ('date_sub', '!=', None),
    #          ('kip_sub', '!=', None),
    #          ('level', '=', None)])
    #     for item in cus_phone_obj:
    #         if item.date_sub and item.kip_sub:
    #             date_sub = datetime.strptime(item.date_sub, '%Y-%m-%d %H:%M:%S')
    #             # kiem tra xem chon ca lam viec nao
    #             if item.kip_sub == 1:
    #                item.create_on = date_sub + timedelta(hours=1)
    #             if item.kip_sub == 2:
    #                item.create_on = date_sub + timedelta(hours=6)
    #             if item.kip_sub == 3:
    #                item.create_on = date_sub + timedelta(hours=9)

    # hung code
    # ----bắt đầu-----
    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            print(vals)
            # không nghe máy stage_id = 109
            if vals['stage_id'] == 2:
                self.partner_id.level = 2
            # tư vấn lần 1 hoặc lần 2
            if vals['stage_id'] == 5:
                self.partner_id.level = 3
            # tư vấn thành công = 40
            if vals['stage_id'] == 4:
                self.partner_id.level = 6
            if vals['stage_id'] == 6:
                self.partner_id.level = 4
        return super(Duoc_Crm_Lead, self).write(vals)
    # ----kết thúc-----



class CrmLeadLostInherit(models.TransientModel):
    _inherit = 'crm.lead.lost'

    @api.multi
    def action_lost_reason_apply(self):
        res = super(CrmLeadLostInherit, self).action_lost_reason_apply()
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        reason_name = self.lost_reason_id.name or ""
        body_html_partner = "<div><ul>" \
                            "<li>Thất Bại</li>" \
                            "<li>{sale_man} : {time}</li>" \
                            "<li>Lý Do: {activity}</li>" \
                            "</ul></div>".format(sale_man=self.env.user.name, time=fields.Date.today(),
                                                 activity=reason_name)
        leads.partner_id.message_post(body_html_partner)
        if self.lost_reason_id and self.lost_reason_id.type_state == 2 and len(leads.partner_id.ids) > 0:
                leads.partner_id.write({'active': False})
        return res


class CrmStageInherit(models.Model):
    _inherit = "crm.stage"
    _sql_constraints = [
        ('type_stage', 'unique (type_state)', 'Loại trạng thái đã tồn tại'),
    ]
    type_state = fields.Selection([
        (1, 'Đơn đã bị huỷ'),
        (2, 'Đơn xác nhận'),
        (3, 'Đơn đang đi trên đường'),
        (4, 'Đơn hàng hoàn thành'),
        (5, 'Đơn hoàn')
    ], string='Loại trạng thái')
        # for rec in obj_crm_lead:
class CrmLeadLostReasonInherit(models.Model):
    _inherit = 'crm.lost.reason'
    _sql_constraints = [
        ('type_stage', 'Check(1=1)', 'Loại lý do đã tồn tại'),
    ]
    type_state = fields.Selection([
        (1, 'Quá Hạn'),
        (2, 'Không tái phân bổ'),
    ], string='Loại')

    @api.constrains('type_state')
    def _check_type_state(self):
        if self.type_state == 1 :
            obj_lost = self.search([('type_state','=',1)])
            if obj_lost :
                raise UserError(_("Loại lý do Quá Hạn đã tồn tại"))
