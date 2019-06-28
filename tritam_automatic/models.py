# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime
from datetime import timedelta
import datetime
from odoo.exceptions import AccessDenied, UserError
# _logger = logging.getLogger(__name__) 


class Duocphanbo(models.Model):
    _name = 'res.automatic'

    @api.multi
    def compute_info(self):
        qty = self.env['res.partner'].search([('date_sub', '=', datetime.datetime.today().date()), ('x_user_id', '=', self.env.user.id)])
        print(qty)
        return "Số lượng KH phân bổ: " + len(qty)

    a = fields.Float()
    compute = fields.Char(default=compute_info, string='Info', readonly=1)

    # Hot line
    @api.multi
    def action_hotline(self):
        partner_obj = self.env['res.partner']
        if self.env.user.category_id:
            list_categ_user = self.env.user.category_id
            sales = self.env.user
            # danh sach cung tag
            list_partner_cungtag = self.env['crm.lead'].search(
                [('type_contact', '=', 'new'),
                 ('user_id', '=', self.env.user.id),
                 ('date_create', '=', datetime.date.today())])
            kh_danhan = len(list_partner_cungtag)  # Khach hang da nhan
            if self.env.user.new_contact <= kh_danhan:
                raise UserError(('Đã nhận đủ số '
                                 'contact tối đa'))
            if 1 == 1:
                partner_phanbo = partner_obj.search(
                    [('category_id', 'in', [x.id for x in list_categ_user if x.name.startswith(u"Hotline" or u"hotline")]),
                     ('allocate', '=', 'yes')],
                    order='create_date desc', limit=1)

                if not partner_phanbo: raise UserError(
                    ('Đã hết contact thỏa mãn điều kiện'))
                if partner_phanbo:
                    for r in partner_phanbo:
                        # r.x_user_id = sales.id
                        # r.date_sub = datetime.datetime.today()
                        r.allocate = 'no'

                        phone = r.phone or ''
                        str_p = ''
                        for cate in r.category_id:
                            if len(str_p) == 0:
                                str_p = cate.name
                            else:
                                str_p = str_p + u', ' + cate.name
                        name_ticket = u'Mới_' + r.name + '_' + phone + '_' + str_p
                        partner_id = r.id
                        user_id = self.env.user.id
                        description = r.comment or ''
                        self.env['crm.lead'].create(
                            vals={'name': name_ticket,
                                  'partner_id': partner_id,
                                  'user_id': user_id,
                                  'type_contact': 'new',
                                  'crm_lead_category_ids':
                                      [(6, 0,[x.id for x in r.category_id])],
                                  'description': description,
                                  'phone': phone,})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Mới
    @api.multi
    def action_in(self):
        # print("helloooooo")
        partner_obj = self.env['res.partner']
        if self.env.user.category_id:
            list_categ_user = self.env.user.category_id.ids
            sales = self.env.user
            # danh sach cung tag
            list_partner_cungtag = self.env['crm.lead'].search([('type_contact', '=', 'new'),('user_id', '=', self.env.user.id),('date_create', '=', datetime.date.today())])
            kh_danhan = len(list_partner_cungtag) # Khach hang da nhan
            if self.env.user.new_contact <= kh_danhan:
                raise UserError(('Đã nhận đủ số contact tối đa'))
            if 1 == 1:
                partner_phanbo = partner_obj.search(
                    [('category_id', 'in', list_categ_user),
                     ('allocate', '=', 'yes')], order='create_date asc',
                    limit=1)

                if not partner_phanbo: raise UserError(('Đã hết contact thỏa mãn điều kiện'))
                if partner_phanbo:
                    for r in partner_phanbo:
                        r.allocate = 'no'
                        phone = r.phone or ''
                        str_p = ''
                        for cate in r.category_id:
                            if len(str_p) == 0:
                                str_p = cate.name
                            else:
                                str_p = str_p + u', ' + cate.name
                        name_ticket = u'Mới_' + r.name + '_' + phone + '_' + str_p
                        partner_id = r.id
                        user_id = self.env.user.id
                        description = r.comment or ''
                        self.env['crm.lead'].create(vals={'name': name_ticket,
                                                          'partner_id': partner_id,
                                                          'user_id': user_id,
                                                          'type_contact': 'new',
                                                          'crm_lead_category_ids': [(6, 0, [x.id for x in r.category_id])],
                                                          'description': description,
                                                          'phone': phone,
                                                          })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Tái sử dụng
    @api.multi
    def action_renew_rp(self):
        partner_obj = self.env['res.partner']
        # if self.env.user.has_group('tritam_users.group_sales_team_manager') and self.env.user.category_id:
        list_categ_user = self.env.user.category_id.ids
        sales = self.env.user
        # danh sach cung tag
        list_partner_cungtag = self.env['crm.lead'].search(
            [('type_contact', '=', 'reuse'),('user_id', '=', self.env.user.id), ('date_create', '=', datetime.date.today())])
        kh_danhan = len(list_partner_cungtag)  # Khach hang da nhan
        if self.env.user.re_contact <= kh_danhan:
            raise UserError(('Đã nhận đủ số contact tối đa'))
        if 1 == 1:
            partner_phanbo = partner_obj.search([
                                                ('reuse', '=', 'yes'),
                                                ('category_id', 'in', list_categ_user)
                                                ], order='create_date desc', limit=1)
            if not partner_phanbo: raise UserError(('Đã hết contact thỏa mãn điều kiện'))
            if partner_phanbo:
                for r in partner_phanbo:
                    # r.x_user_id = sales.id
                    # r.date_sub = datetime.datetime.today()
                    r.reuse = 'no'

                    phone = r.phone or ''
                    str_p = ''
                    for cate in r.category_id:
                        if len(str_p) == 0:
                            str_p = cate.name
                        else:
                            str_p = str_p + u', ' + cate.name
                    name_ticket = u'Tái sử dụng_' + r.name + '_' + phone + '_' + str_p
                    partner_id = r.id
                    user_id = self.env.user.id
                    description = r.comment or ''
                    self.env['crm.lead'].create(vals={'name': name_ticket,
                                                      'partner_id': partner_id,
                                                      'user_id': user_id,
                                                      'type_contact': 'reuse',
                                                      'crm_lead_category_ids': [(6, 0, [x.id for x in r.category_id])],
                                                      'description': description,
                                                      'phone': phone,
                                                      })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Tái sử dụng sau 18h
    @api.multi
    def action_18h(self):
        partner_obj = self.env['res.partner']
        # if self.env.user.has_group('tritam_users.group_sales_team_manager') and self.env.user.category_id:
        list_categ_user = self.env.user.category_id.ids
        sales = self.env.user
        # danh sach cung tag
        list_partner_cungtag = self.env['crm.lead'].search(
            [('type_contact', '=', 'new'), ('user_id', '=', self.env.user.id),
             ('date_create', '=', datetime.date.today())])
        kh_danhan = len(list_partner_cungtag)  # Khach hang da nhan
        if self.env.user.re_contact <= kh_danhan:
            raise UserError(('Đã nhận đủ số contact tối đa'))
        if 1 == 1:
            partner_phanbo = partner_obj.search([
                ('reuse', '=', 'yes'),
                ('category_id', 'in', list_categ_user)
            ], order='create_date desc', limit=1)
            if not partner_phanbo: raise UserError(
                ('Đã hết contact thỏa mãn điều kiện'))
            if partner_phanbo:
                for r in partner_phanbo:
                    # r.x_user_id = sales.id
                    # r.date_sub = datetime.datetime.today()
                    r.reuse = 'no'

                    phone = r.phone or ''
                    str_p = ''
                    for cate in r.category_id:
                        if len(str_p) == 0:
                            str_p = cate.name
                        else:
                            str_p = str_p + u', ' + cate.name
                    name_ticket = u'Tái SD sau 18_' + \
                                  r.name + '_' \
                                  + phone + '_' + str_p
                    partner_id = r.id
                    user_id = self.env.user.id
                    description = r.comment or ''
                    self.env['crm.lead'].create(vals={'name': name_ticket,
                                                      'partner_id': partner_id,
                                                      'user_id': user_id,
                                                      'type_contact': 'reuse',
                                                      'crm_lead_category_ids': [
                                                          (6, 0, [x.id for x in
                                                                  r.category_id])],
                                                      'description': description,
                                                      'phone': phone,
                                                      })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Tai ky
    @api.multi
    def action_to_sign(self):
        partner_obj = self.env['res.partner']
        # if self.env.user.has_group('tritam_users.group_sales_team_manager') and self.env.user.category_id:
        list_categ_user = self.env.user.category_id.ids
        # danh sach cung tag
        list_partner_cungtag = self.env['crm.lead'].search(
            [('type_contact', '=', 'contract'),
             ('user_id', '=', self.env.user.id),
            ('date_create', '=', datetime.date.today())])
        kh_danhan = len(list_partner_cungtag)  # Khach hang da nhan
        if self.env.user.re_sign <= kh_danhan:
            raise UserError(('Đã nhận đủ số contact tối đa'))
        if 1 == 1:
            partner_phanbo = partner_obj.search([
                                                # ('x_user_id', '=', None),
                                                ('to_sign', '=', 'yes'),
                                                ('category_id', 'in', list_categ_user),
                                                ('reuse', '=', 'no'),
                                                ], order='create_date desc', limit=1)
            if not partner_phanbo: raise UserError(('Đã hết contact thỏa mãn điều kiện'))
            if partner_phanbo:
                for r in partner_phanbo:
                    # r.x_user_id = sales.id
                    r.date_sub = datetime.datetime.today()
                    r.to_sign = 'no'

                    phone = r.phone or ''
                    str_p = ''
                    for cate in r.category_id:
                        if len(str_p) == 0:
                            str_p = cate.name
                        else:
                            str_p = str_p + u', ' + cate.name
                    name_ticket = u'Tái ký_' + r.name + '_' + phone + '_' + str_p
                    partner_id = r.id
                    user_id = self.env.user.id
                    description = r.comment or ''
                    self.env['crm.lead'].create(vals={'name': name_ticket,
                                                      'partner_id': partner_id,
                                                      'user_id': user_id,
                                                      'type_contact': 'contract',
                                                      'crm_lead_category_ids': [(6, 0, [x.id for x in r.category_id])],
                                                      'description': description,
                                                      'phone': phone,
                                                      })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Nhan cts Tai ky lai
    @api.multi
    def action_to_sign_recall(self):
        partner_obj = self.env['res.partner']
        # if self.env.user.has_group('tritam_users.group_sales_team_manager') and self.env.user.category_id:
        list_categ_user = self.env.user.category_id.ids
        sales = self.env.user
        # danh sach cung tag
        list_partner_cungtag = self.env['crm.lead'].search(
            [('type_contact', '=', 'contract'), ('user_id', '=', self.env.user.id), ('date_create', '=', datetime.date.today())])
        kh_danhan = len(list_partner_cungtag)  # Khach hang da nhan

        if self.env.user.re_sign <= kh_danhan:
            raise UserError(('Đã nhận đủ số contact tối đa'))
        if 1 == 1:
            partner_phanbo = partner_obj.search([
                ('to_sign', '=', 'yes'),
                ('reuse', '=', 'yes'),
                ('category_id', 'in', list_categ_user)],
                order='create_date asc', limit=1)
            if not partner_phanbo: raise UserError(('Đã hết contact thỏa mãn điều kiện'))
            if partner_phanbo:
                for r in partner_phanbo:
                    # r.x_user_id = sales.id
                    # r.date_sub = datetime.datetime.today()
                    r.to_sign = 'no'
                    r.reuse = 'no'
                    phone = r.phone or ''
                    str_p = ''
                    for cate in r.category_id:
                        if len(str_p) == 0:
                            str_p = cate.name
                        else:
                            str_p = str_p + u', ' + cate.name
                    name_ticket = u'Tái ký lại_' + r.name + '_' + phone + '_' + str_p
                    partner_id = r.id
                    user_id = self.env.user.id
                    description = r.comment or ''
                    self.env['crm.lead'].create(vals={'name': name_ticket,
                                                      'partner_id': partner_id,
                                                      'user_id': user_id,
                                                      'type_contact': 'contract',
                                                      'crm_lead_category_ids': [(6, 0, [x.id for x in r.category_id])],
                                                      'description': description,
                                                      'phone': phone,
                                                      })
                    partner_phanbo.update(
                        {'category_id': [(6, 0, [13])]})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Nhan cham soc
    @api.multi
    def action_to_sp(self):
        a = 1
        partner_obj = self.env['res.partner']
        # if self.env.user.has_group('tritam_users.group_sales_team_manager') and self.env.user.category_id:
        list_categ_user = self.env.user.category_id.ids
        sales = self.env.user
        # danh sach cung tag
        list_partner_cungtag = self.env['crm.lead'].search(
            [('type_contact', '=', 'sp'),('user_id', '=', self.env.user.id), ('date_create', '=', datetime.date.today())])
        kh_danhan = len(list_partner_cungtag)  # Khach hang da nhan
        if self.env.user.re_sp <= kh_danhan:
            raise UserError(('Đã nhận đủ số contact tối đa'))
        if 1 == 1:
            partner_phanbo = partner_obj.search([
                                                # ('x_user_id', '=', None),
                                                ('to_support', '=', 'yes'),
                                                ('reuse', '=', 'no'),
                                                 ('category_id', 'in', list_categ_user)
                                                ], order='create_date desc', limit=1)
            if not partner_phanbo: raise UserError(('Đã hết contact thỏa mãn điều kiện'))
            if partner_phanbo:
                for r in partner_phanbo:
                    # r.x_user_id = sales.id
                    # r.date_sub = datetime.datetime.today()
                    r.to_support = 'no'

                    phone = r.phone or ''
                    str_p = ''
                    for cate in r.category_id:
                        if len(str_p) == 0:
                            str_p = cate.name
                        else:
                            str_p = str_p + u', ' + cate.name
                    name_ticket = u'Chăm sóc_' + r.name + '_' + phone + '_' + str_p
                    partner_id = r.id
                    user_id = self.env.user.id
                    description = r.comment or ''
                    self.env['crm.lead'].create(vals={'name': name_ticket,
                                                      'partner_id': partner_id,
                                                      'user_id': user_id,
                                                      'type_contact': 'sp',
                                                      'crm_lead_category_ids': [(6, 0, [x.id for x in r.category_id])],
                                                      'description': description,
                                                      'phone': phone,
                                                      })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Nhan cts tai cham soc
    @api.multi
    def action_to_support_need_sp(self):
        a = 1
        partner_obj = self.env['res.partner']
        # if self.env.user.has_group('tritam_users.group_sales_team_manager') and self.env.user.category_id:
        list_categ_user = self.env.user.category_id.ids
        sales = self.env.user
        # danh sach cung tag
        list_partner_cungtag = self.env['crm.lead'].search(
            [('type_contact', '=', 'sp'),
             ('user_id', '=', self.env.user.id),
             ('date_create', '=', datetime.date.today())])
        kh_danhan = len(list_partner_cungtag)  # Khach hang KNM
        if self.env.user.re_sp <= kh_danhan:
            raise UserError(('Đã nhận đủ số contact tối đa'))
        if 1 == 1:
            partner_phanbo = partner_obj.search([
                ('to_support', '=', 'yes'),
                ('reuse', '=', 'yes'),
                ('category_id', 'in', list_categ_user)
            ], order='create_date asc', limit=1)
            if not partner_phanbo: raise UserError(
                ('Đã hết contact thỏa mãn điều kiện'))
            if partner_phanbo:
                for r in partner_phanbo:
                    # r.x_user_id = sales.id
                    # r.date_sub = datetime.datetime.today()
                    r.to_support = 'no'
                    r.reuse = 'no'
                    phone = r.phone or ''
                    str_p = ''
                    for cate in r.category_id:
                        if len(str_p) == 0:
                            str_p = cate.name
                        else:
                            str_p = str_p + u', ' + cate.name
                    name_ticket = u'Tái chăm sóc_' + r.name + '_' + phone + '_' + str_p
                    partner_id = r.id
                    user_id = self.env.user.id
                    description = r.comment or ''

                    self.env['crm.lead'].create(vals={'name': name_ticket,
                                                      'partner_id': partner_id,
                                                      'user_id': user_id,
                                                      'type_contact': 'sp',
                                                      'crm_lead_category_ids': [(6, 0, [x.id for x in r.category_id])],
                                                      'description': description,
                                                      'phone': phone,
                                                      })
                    partner_phanbo.update({'category_id': [(6, 0, [13])]})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class respartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def schedule_support(self):
        lead_date = self.env['history.lead'].search([('date_schedule', '=', datetime.date.today())])
        if self.env['crm.stage'].search([('type_call', '=', True)]):
            obj = self.env['crm.stage'].search([('type_call', '=', True)])[0]
            for r in lead_date:
                r.lead_id.stage_id = obj
                r.lead_id.date_action = datetime.date.today()


    @api.model
    def check_number_use(self):
        number = self.env['ir.values'].sudo().get_default(
            'sale.config.settings', 'number_use') or 1
        sql = """
            select * from (
                select count(partner_id) numbers, partner_id from crm_lead where type_contact = 'reuse'
                group by partner_id
                ) as tab where numbers >= %d
        """ % (number)
        self.env.cr.execute(sql)
        data = self.env.cr.dictfetchall()
        for r in data:
            self.browse(r.get('partner_id')).state_reuse = 'yes'


    @api.model
    def schedule_date(self):
        a = 1
        # obj_res_partner = self.search([('x_user_id', '!=', None), ('level', 'in', [1]), ('date_sub', '!=', None)])
        # for record in obj_res_partner:
        #     if (datetime.datetime.today() - datetime.datetime.strptime(record.date_sub, "%Y-%m-%d")).days > 3:
        #         record.nguon = 3
        #         record.x_user_id = None
        #         record.date_sub = None
        #
        # obj_res_partner = self.search([('x_user_id', '!=', None), ('level', 'in', [2]), ('date_sub', '!=', None)])
        # for record in obj_res_partner:
        #     if (datetime.datetime.today() - datetime.datetime.strptime(record.date_sub, "%Y-%m-%d")).days > 3:
        #         record.nguon = 3
        #         record.x_user_id = None
        #         record.date_sub = None
        #
        # obj_res_partner = self.search([('x_user_id', '!=', None), ('level', 'in', [3]), ('date_sub', '!=', None)])
        # for record in obj_res_partner:
        #     if (datetime.datetime.today() - datetime.datetime.strptime(record.date_sub, "%Y-%m-%d")).days > 10:
        #         record.nguon = 3
        #         record.x_user_id = None
        #         record.date_sub = None
        # # print "===============Remove======================="
        # return {'edit': 'done'}
