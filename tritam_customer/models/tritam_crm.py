# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
import datetime
from odoo.exceptions import UserError


class history_lead(models.Model):
    _name = 'history.lead'
    _description = 'History'

    lead_id = fields.Many2one('crm.lead', required=True)
    date_schedule = fields.Date(required=True)


class tritam_crm_lead(models.Model):
    _inherit = 'crm.lead'

    name = fields.Char('Opportunity', required=True, index=True,track_visibility='onchange')
    crm_lead_category_ids = fields.Many2many('res.partner.category', 'crm_category_rel', 'lead_id', 'category_id',string='Tag')
    # next_activity_id = fields.Many2one("crm.activity", string="Next Activity", index=True , compute ='_compute_next_activity_id')
    type_contact = fields.Selection([
        ('new', 'Contact mới'),
        ('reuse', 'Contact tái sử dụng'),
        ('contract', 'Contact tái ký'),
        ('sp', 'Contact CSKH')
    ],track_visibility='onchange', string='Loại contact')
    description = fields.Text('Notes',track_visibility='onchange')
    history_ids = fields.One2many('history.lead', 'lead_id')
    x_product_id = fields.Many2one('product.product', related='partner_id.x_product_id', string='Sản Phẩm',
                                   readonly=True)
    source_id = fields.Many2one('utm.source', string='Source',related='partner_id.utm_id',
                                help="This is the link source, e.g. Search Engine, another domain,or name of email list")

    level_kh = fields.Selection(related='partner_id.level', string='Level', store=True)

    # @api.one
    # @api.depends('partner_id')
    # def _compute_next_activity_id(self):
    #     id_activity = self.env['crm.activity'].search([('x_stage', '=', self.partner_id.level)], limit=1).id
    #     self.next_activity_id = id_activity

    @api.model
    def _onchange_stage_id_values(self, stage_id):
        """ returns the new values when stage_id has changed """
        # if self.partner_id:
        #     if self.partner_id.level == 1:
        #         self.partner_id.level = 2
        #     else:
        #         self.partner_id.level = 3
        if not stage_id:
            return {}
        stage = self.env['crm.stage'].browse(stage_id)
        if stage.on_change:
            return {'probability': stage.probability}
        return {}

    @api.model
    def create(self, vals):
        res = super(tritam_crm_lead, self).create(vals)
        category_id = ""
        body_html_partner = ""
        if 'crm_lead_category_ids' in vals and len(vals['crm_lead_category_ids']) > 0:
                arr_cat = [x for x in vals['crm_lead_category_ids'][0][2]]
                obj_tag = self.crm_lead_category_ids.browse(arr_cat)
                for r in obj_tag:
                    category_id += r.name +","
                category_id = ("<li>Tag : "+ category_id + "</li>")
        body_html_partner += "<div><ul>" \
                            "<li>Tạo mới </li>" \
                            "{category_id}" \
                            "</ul></div>".format(category_id=category_id)
        res.message_post(body_html_partner)
        return res

    @api.multi
    def write(self, vals):
        # stage change: update date_last_stage_update
        old_state = ""
        body_html_partner = ""
        if self.stage_id:
            old_state = self.stage_id.name
        if 'stage_id' in vals:
            stage_name = self.stage_id.browse([int(vals['stage_id'])]).name
            name =("<li>Trạng Thái Ticket: "+old_state+" --> "+stage_name+"</li>")
            body_html_partner += "<div><ul>" \
                                "<li>{sale_man} : {time}</li>" \
                                "<li>Chỉnh sửa</li>" \
                                "{name}" \
                                "</ul></div>".format(sale_man=self.env.user.name,
                                                     time=fields.Date.today(),
                                                     name=name)
            self.partner_id.message_post(body_html_partner)
        if 'crm_lead_category_ids' in vals and len(vals['crm_lead_category_ids']) > 0:
            arr_cat = [x for x in vals['crm_lead_category_ids'][0][2]]
            obj_tag = self.crm_lead_category_ids.browse(arr_cat)
            cat = ""
            old_cat = ""
            body_html_partner = ""
            for rec in obj_tag:
                cat += rec.name + ","
            if len(self.crm_lead_category_ids.ids) > 0:
                for i in self.crm_lead_category_ids:
                    old_cat += i.name.encode('utf-8') + ","
            else:
                old_cat = ""
            category_id = ("<li>Tag : " + old_cat + " -->" + cat + "</li>")
            body_html_partner += "<div><ul>" \
                                "<li>Chỉnh sửa </li>" \
                                "{category_id}" \
                                "</ul></div>".format(category_id=category_id)
            self.message_post(body_html_partner)
        return super(tritam_crm_lead, self).write(vals)


class CRMStage(models.Model):
    _inherit = 'crm.stage'

    type_call = fields.Boolean(string=u'Cần chăm sóc trong ngày', default=False)
    type_called = fields.Boolean(string=u'Đã chăm sóc', default=False)



# class ActivityLog(models.TransientModel):
#     _inherit = 'crm.activity.log'
#
#     numbers = fields.Integer(string=u'Số lần')
#     to_date = fields.Date(string=u'Tới ngày')
#
#     time_begin = fields.Char(string='Time Begin')
#     duration = fields.Char(string='Duration')
#
#     level = fields.Selection([
#         (1, 'Level 1'),
#         (2, 'Level 2'),
#         (3, 'Level 3'),
#         (4, 'Level 4'),
#         (5, 'Level 5'),
#         (6, 'Level 6'),
#         (7, 'Level 7'),
#         (8, 'Level 8'),
#     ], string='Level')
#
#     @api.multi
#     def action_schedule(self):
#         for log in self:
#             if log.lead_id.history_ids:
#                 log.lead_id.history_ids.unlink()
#             if log.numbers == 0 and not log.to_date:
#                 UserError(('Cấu hình sai'))
#             if log.numbers != 0 and log.to_date:
#                 UserError(('Cấu hình sai'))
#             if log.numbers > 0:
#                 so_ngay = log.recommended_activity_id.days
#                 date = datetime.date.today()
#                 for r in range(0, log.numbers):
#                     self.env['history.lead'].create(vals={'lead_id': log.lead_id.id, 'date_schedule': date})
#                     date = date + datetime.timedelta(days=so_ngay)
#             if log.to_date:
#                 so_ngay = log.recommended_activity_id.days
#                 date = datetime.date.today()
#                 for r in range(0, 99):
#                     self.env['history.lead'].create(vals={'lead_id': log.lead_id.id, 'date_schedule': date})
#                     date = date + datetime.timedelta(days=so_ngay)
#                     if datetime.datetime.strptime(str(date), '%Y-%m-%d') > datetime.datetime.strptime(log.to_date, '%Y-%m-%d'):
#                         break
#             log.lead_id.write({
#                 'title_action': log.title_action,
#                 'date_action': log.date_action,
#                 'next_activity_id': log.next_activity_id.id,
#             })
#             next_activity = ""
#             date_action = ""
#             title_action = ""
#             recommended_activity = ""
#             numbers = ""
#             to_date = ""
#             body_html_partner = ""
#             if self.next_activity_id:
#                 next_activity = ("<li>Hoạt động tiếp theo: " + self.next_activity_id.name + "</li>")
#             if self.date_action:
#                 date_action = ("<li>Ngày hoạt động tiếp theo: " + self.date_action + "</li>")
#             if self.title_action:
#                 title_action = ("<li>Tóm Tắt: " + self.title_action + "</li>")
#             if self.recommended_activity_id:
#                 recommended_activity = ("<li>Recommended activities: " + self.recommended_activity_id.name + "</li>").encode('utf-8')
#             if self.numbers:
#                 numbers = ("<li>Số lần : " + str(self.numbers) + "</li>").encode('utf-8')
#             if self.to_date:
#                 to_date = ("<li>Tới Ngày: " + self.to_date+ "</li>").encode('utf-8')
#             body_html_partner += "<div><ul>" \
#                                 "<li>{sale_man} : {time}</li>" \
#                                 "<li>Schedule Next  </li>" \
#                                 "{next_activity}" \
#                                 "{date_action}" \
#                                 "{title_action}" \
#                                 "{recommended_activity}" \
#                                 "{numbers}" \
#                                 "{to_date}" \
#                                 "</ul></div>".format(sale_man=self.env.user.name.encode('utf-8'),
#                                                      time=fields.Date.today(),
#                                                      next_activity=next_activity,
#                                                      date_action=date_action, title_action=title_action,
#                                                      recommended_activity=recommended_activity, numbers=numbers, to_date=to_date)
#             log.lead_id.partner_id.message_post(body_html_partner)
#         return True
#
#     @api.multi
#     def action_log_and_schedule(self):
#         self.ensure_one()
#         self.action_log()
#         for r in self:
#             if r.level and r.lead_id.partner_id:
#                 r.lead_id.partner_id.level = r.level
#         view_id = self.env.ref('crm.crm_activity_log_view_form_schedule')
#         return {
#             'name': ('Next activity'),
#             'res_model': 'crm.activity.log',
#             'context': {
#                 'default_last_activity_id': self.next_activity_id.id,
#                 'default_lead_id': self.lead_id.id
#             },
#             'type': 'ir.actions.act_window',
#             'view_id': False,
#             'views': [(view_id.id, 'form')],
#             'view_mode': 'form',
#             'target': 'new',
#             'view_type': 'form',
#             'res_id': False
#         }
#
#     @api.multi
#     def action_log(self):
#         for r in self:
#             if self.env['crm.stage'].search([('type_call', '=', True)]):
#                 call = self.env['crm.stage'].search([('type_call', '=', True)])[0]
#                 called = self.env['crm.stage'].search([('type_called', '=', True)])[0]
#                 if r.lead_id.stage_id.type_call == True and called:
#                     r.lead_id.stage_id = called
#             if r.level and r.lead_id.partner_id:
#                 r.lead_id.partner_id.level = r.level
#             acityvity_name = r.next_activity_id.name or ""
#             title_action = r.title_action or ""
#             note = r.note or ""
#             body_html_partner = "<div><ul>" \
#                                 "<li>{sale_man} : {time}</li>" \
#                                 "<li>Tạo hoạt động mới: {activity}</li>" \
#                                 "<li>Tóm tắt: {cmt}</li>" \
#                                 "<li>Note: {note}</li>" \
#                                 "</ul></div>".format(sale_man=r.env.user.name.encode('utf-8'),time=fields.Date.today(),activity=acityvity_name.encode('utf-8'),cmt=title_action.encode('utf-8'),note=note.encode('utf-8'))
#             r.env['res.partner'].browse(r.lead_id.partner_id.id).message_post(body_html_partner)
#         for log in self:
#             if log.next_activity_id.x_stage == 5:
#                 body_html = "<div><b>%(title)s</b>: %(next_activity)s</div><div><b>Time Begin :</b> %(time_begin)s</div><div><b>Duration :</b> %(duration)s</div>%(description)s%(note)s" % {
#                     'title': _('Activity Done'),
#                     'next_activity': log.next_activity_id.name,
#                     'description': log.title_action and '<p><em>%s</em></p>' % log.title_action or '',
#                     'note': log.note or '',
#                     'time_begin':log.time_begin or '',
#                     'duration' : log.duration  or '',
#                 }
#             else:
#                 body_html = "<div><b>%(title)s</b>: %(next_activity)s</div>%(description)s%(note)s" % {
#                     'title': _('Activity Done'),
#                     'next_activity': log.next_activity_id.name,
#                     'description': log.title_action and '<p><em>%s</em></p>' % log.title_action or '',
#                     'note': log.note or '',
#                 }
#             log.lead_id.message_post(body_html, subject=log.title_action, subtype_id=log.next_activity_id.subtype_id.id)
#             log.lead_id.write({
#                 'date_deadline': log.date_deadline,
#                 'planned_revenue': log.planned_revenue,
#                 'title_action': False,
#                 'date_action': False,
#                 'next_activity_id': False,
#             })
#         return True
#
# class Tritam_CrmActivity(models.Model) :
#     _inherit = 'crm.activity'
#     _sql_constraints = [('x_stage', 'unique(x_stage)', 'Không được nhập trùng các stage')]
#
#     x_stage = fields.Integer(string='Stage')




