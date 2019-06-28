# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError
import datetime
import sys
import re
#reload(sys)
#sys.setdefaultencoding("utf8")


class NguonPartner(models.Model):
    _name = 'nguon.partner'
    _rec_name = 'name'

    name = fields.Char(string=u'Nguồn')


class tritam_res_partner(models.Model):
    _inherit = 'res.partner'
    _sql_constraints = [('email_uniq', 'unique(email)', 'Email Đã Tồn Tại'),
                        ('cmtnd_uniq', 'unique(cmtnd)', 'Chứng Minh Thư Nhân Dân Đã Tồn Tại'),
                        ('phone_uniq', 'Check(1=1)', 'Số Điện Thoại Đã Tồn Tại'),
                        ('mobile_uniq', 'Check(1=1)','Số Di Động Đã Tồn Tại')]

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
                                                  string="Account Payable", oldname="property_account_payable",
                                                  domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
                                                  help="This account will be used instead of the default one as the payable account for the current partner",
                                                  required=False)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                                     string="Account Receivable", oldname="property_account_receivable",
                                                     domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
                                                     help="This account will be used instead of the default one as the receivable account for the current partner",
                                                     required=False)
    # type_knm = fields.Selection(
    #     [(1, 'KNM New'), (2, 'KNM Reuse'), (3, 'KNM CSKH'), (4, 'KNM')],
    #     string="type KNM", invisible=True, default = 1)

    mskh = fields.Char('Mã Số Khách Hàng',readonly=True)
    cmtnd = fields.Char('CMTND')
    level = fields.Selection([
        (1, 'Level 1'),
        (2, 'Level 2'),
        (22, 'Level 2.2'),
        (3, 'Level 3'),
        (4, 'Level 4'),
        (42, 'Level 4.2'),
        (5, 'Level 5'),
        (6, 'Level 6'),
        (7, 'Level 7'),
        (8, 'Level 8'),
    ], string='Level')
    nguon = fields.Selection([
        (1, 'Marketing'),
        (2, 'Khác '),
        (3, 'Tái sử dụng'),
    ], string='Nguồn ', default = 1,readonly=True)
    dublicate = fields.Boolean('Bị Trùng', default = False)
    age_cts = fields.Integer(string='Tuổi khách hàng')


    @api.model
    def domain_source_customer(self):
        obj_source_customer = self.env['customer.source'].search([])
        arr_parent_id = []
        for rec in obj_source_customer:
            arr_parent_id.append(rec.parent_id.id)
        return [('id', 'not in', arr_parent_id),('x_active', '=', True)]
    nguon_khac = fields.Many2one('nguon.partner')

    date_sub = fields.Datetime(string=u'Ngày phân bổ')
    # kip_sub = fields.Selection([(1, 'Sáng'),(2,'Chiều'),(3,'Tối')], string='Ca làm việc', default=1)

    str_category = fields.Char(compute='compute_str_cate')
    source_customer = fields.Many2one('customer.source','Nguồn',domain=domain_source_customer)
    team_marketing = fields.Many2one('hr.department', related='source_customer.team_marketing', string='Team Marketing', readonly=True)
    create_by = fields.Many2one('res.users', string='Người nhập')
    create_on = fields.Datetime(string='Ngày nhập')

    allocate = fields.Selection([('yes', 'Có'), ('no', 'Không')], string='Cần phân bổ', default='yes')
    reuse = fields.Selection([('yes', 'Có'), ('no', 'Không')], string='Cần tái sử dụng', default='no')
    to_sign = fields.Selection([('yes', 'Có'), ('no', 'Không')], string='Cần tái ký', default='no')
    to_support = fields.Selection([('yes', 'Có'), ('no', 'Không')], string='Cần chăm sóc', default='no')
    state_reuse = fields.Selection([('yes', 'Hết lượt tái SD'), ('no', 'Còn')], string='Hết lượt tái sử dụng', default='no')
    detail_support_ids = fields.One2many('tritam_detail_support', 'parent_id', 'Chi tiết chăm sóc')
    x_product_id = fields.Many2one('product.product',related='source_customer.x_product_id', string='Sản Phẩm', readonly=True)
    utm_id = fields.Many2one('utm.source',related='source_customer.utm_id', string='Kênh marketing', readonly=True)

    # phân quyền không được sửa lại đoạn
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        ##############################phân quyền không sửa đoạn này ####################################
        if len(name) >= 10\
                and len(name) <= 13 \
                and self.is_number(name) is True \
                and name.isdigit() is True \
                and name == name.strip():
            recs = self.search(['|', ('mobile', '=', name), ('phone', '=', name)] + args, limit=limit)
        ###############################################################################################
        else :
            recs = self.search(['|',('name', operator, name),('phone', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.constrains('phone', 'mobile')
    def _check_phone_is_number(self):
        if self._context.get('check_contact'):
            return
        obj_phone = self.search(['|', ('mobile', '=', self.phone), ('phone', '=', self.phone)])|self.search(['|', ('mobile', '=', self.phone), ('phone', '=', self.phone),('active','=',False)])
        phone_ids = obj_phone - self
        if self.mobile:
            if len(self.mobile) < 10 \
                    or len(self.mobile) > 13 \
                    or self.is_number(self.mobile) is False \
                    or self.mobile.isdigit() is False \
                    or self.mobile != self.mobile.strip():
                raise UserError(
                    _("Số Di Động Này Không Đúng (Số điện thoại bao gồm số 0 ở trước, không bao gồm chữ cái, dấu cách, chỉ gồm 10 - 13 số)"))
            obj_mobile = self.search(['|', ('mobile', '=', self.mobile), ('phone', '=', self.mobile)])
            mobile_ids = obj_mobile - self
            phone_ids = phone_ids | mobile_ids
        if phone_ids:
            for phone in phone_ids:
                if self.x_product_id.id is False or self.x_product_id.id != phone.x_product_id.id:
                    self.dublicate = True
                    phone.dublicate = True
                    # self.allocate = 'yes'
                    self.message_post(body="Bị Trùng :{contact},{source},{team},{product} ".format(contact=phone.name,
                                                                                                   source=phone.source_customer.name or "",
                                                                                                   team=phone.team_marketing.name or "",
                                                                                                   product=phone.x_product_id.name or ""))
                else:
                    if self.team_marketing.id and self.team_marketing.id == phone.team_marketing.id:
                        raise UserError(_(
                            "Khách hàng này đã tồn tại có cùng Sản Phẩm và cùng Team Marketing"))
                    else:
                        self.dublicate = True
                        phone.dublicate = True
                        # self.allocate = 'yes'
                        self.message_post(
                            body="Bị Trùng :{contact},{source},{team},{product} ".format(contact=phone.name,
                                                                                         source=phone.source_customer.name or "",
                                                                                         team=phone.team_marketing.name or "",
                                                                                         product=phone.x_product_id.name or ""))
        if len(self.phone) < 10 \
                or len(self.phone) > 13 \
                or self.is_number(self.phone) is False \
                or self.phone.isdigit() is False \
                or self.phone != self.phone.strip():
            raise UserError(
                _("Số Di Động Này Không Đúng (Số điện thoại bao gồm số 0 ở trước, không bao gồm chữ cái, dấu cách, chỉ gồm 10 - 13 số)"))
    @api.multi
    def compute_str_cate(self):
        for r in self:
            str_p = ''
            if r.category_id:
                for cate in r.category_id:
                    if len(str_p) == 0:
                        str_p = cate.name
                    else:
                        str_p = str_p + ', ' + cate.name
                r.str_category = str_p

    @api.model
    def create(self, vals):
        sale = self.env.user.has_group('tritam_users.group_sales_team_manager')
        # group_contact = self.env.user.has_group('tritam_users.group_contact')
        if self.env.user.id != self.env.ref('base.user_root').id:
            if sale:
                if vals.get('x_user_id', False) is False:
                    vals['x_user_id'] = self.env.user.id
        if self._context.get('search_default_customer'):
            vals['mskh'] = self.env['ir.sequence'].get('res.partner.code.fix')
        partner = super(tritam_res_partner, self).create(vals)
        partner.create_by = self.env.user.id
        partner.create_on = datetime.datetime.today()
        adress = ""
        phone = ""
        category_id = ""
        source_customer=""
        comment=""
        mobile =""
        body_html_partner = ""
        if 'street' in vals and vals['street'] :
            adress =  ("<li>Địa chỉ: "+ vals['street'] + "</li>")
        if 'comment' in vals and vals['comment'] :
            comment =  ("<li>Ghi chú ban đầu: "+ vals['comment'] + "</li>")
        if 'phone' in vals and vals['phone']:
            phone = ("<li>Điện Thoại: "+ vals['phone'] + "</li>")
        if 'mobile' in vals and vals['mobile']:
            mobile = ("<li>Di Động: "+ vals['mobile'] + "</li>")
        if 'source_customer' in vals and vals['source_customer']:
            source_customer =  ("<li>Nguồn: "+self.source_customer.browse([int(vals['source_customer'])]).name_get()[0][1] + "</li>")
        if 'category_id' in vals and len(vals['category_id']) > 0:
                arr_cat = [x for x in vals['category_id'][0][2]]
                obj_tag = self.category_id.browse(arr_cat)
                for r in obj_tag:
                    category_id += r.name +","
                category_id = ("<li>Tag  : "+ category_id + "</li>")
        body_html_partner += "<div><ul>" \
                            "<li>{sale_man} : {time}</li>" \
                            "<li>Tạo mới </li>" \
                            "<li>Tên: {name}</li>" \
                            "{adress}" \
                            "{category_id}" \
                            "{source_customer}" \
                            "{phone}" \
                            "{mobile}" \
                            "{comment}" \
                            "</ul></div>".format(sale_man=self.env.user.name, time=fields.Date.today(),
                                                 name=vals['name'],
                                                 adress=adress,category_id=category_id,source_customer=source_customer,phone=phone,comment=comment,mobile=mobile)
        partner.message_post(body_html_partner)
        return partner

    @api.multi
    def write(self, vals):
        flag = False
        for r in self:
            name = ""
            adress = ""
            phone = ""
            mobile = ""
            category_id = ""
            source_customer = ""
            comment=""
            active = ""
            sms = ""
            body_html_partner = ""
            self.message_post(body="")
            if 'name' in vals and vals['name']:
                name =("<li>Tên: "+r.name+" -->"+vals['name']+"</li>")
                flag = True
            if 'street' in vals and vals['street']:
                old_street = r.street or  ""
                adress =("<li>Địa chỉ: "+old_street+" -->"+vals['street']+"</li>")
                flag = True
            if 'phone' in vals and vals['phone']:
                old_phone = r.phone or ""
                phone =("<li>Điện Thoại: "+old_phone+" -->"+vals['phone']+"</li>")
                flag = True
            if 'mobile' in vals and vals['mobile']:
                old_mobile = r.mobile or ""
                mobile =("<li>Di Động: "+old_mobile+" -->"+vals['mobile']+"</li>")
                flag = True
            if 'comment' in vals and vals['comment']:
                old_comment = r.comment or ""
                comment =("<li>Ghi chú ban đầu: "+old_comment+" -->"+vals['comment']+"</li>")
                flag = True
            if 'active' in vals:
                old_active = str(r.active) or ""
                active =("<li>Kích Hoạt: "+old_active+" -->"+str(vals['active'])+"</li>")
                flag = True
            if 'source_customer' in vals and vals['source_customer']:
                source = r.source_customer.browse([int(vals['source_customer'])]).name_get()[0][1]
                if len(r.source_customer.ids) > 0 :
                    old_source = r.source_customer.name_get()[0][1]
                else:
                    old_source = ""
                source_customer = ("<li>Nguồn: "+old_source+" -->"+source+"</li>")
                flag = True
            if 'category_id' in vals and len(vals['category_id']) > 0:
                arr_cat = [x for x in vals['category_id'][0][2]]
                obj_tag = self.category_id.browse(arr_cat)
                cat = ""
                old_cat = ""
                for rec in obj_tag:
                    cat += rec.name + ","
                if len(r.category_id.ids) > 0 :
                    for i in r.category_id :
                        old_cat += i.name +","
                else:
                    old_cat = ""
                category_id = ("<li>Tag : "+old_cat+" -->"+cat+"</li>")
                flag = True
            body_html_partner += "<div><ul>" \
                                "<li>{sale_man} : {time}</li>" \
                                "<li>Chỉnh sửa </li>" \
                                "{active}" \
                                "{name}" \
                                "{adress}" \
                                "{category_id}" \
                                "{source_customer}" \
                                "{phone}" \
                                "{mobile}" \
                                "{comment}" \
                                "</ul></div>".format(sale_man=self.env.user.name,
                                                     time=fields.Date.today(),
                                                     name=name,
                                                     adress=adress, category_id=category_id,active=active,
                                                     source_customer=source_customer, phone=phone,comment=comment,mobile=mobile)
            if flag and self._context.get('check_contact') != True :
                r.message_post(body_html_partner)
        partner = super(tritam_res_partner, self).write(vals)
        return partner

    x_user_id = fields.Many2one('res.users', 'Telesales')


    @api.onchange('x_user_id')
    def onchange_user_sale(self):
        if self.x_user_id:
            if self.level is None or self.level is False:
                self.level = 1


    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            return {'domain': {'state_id': [('code_provine', '=', self.country_id.code)]}}
        else:
            return {'domain': {'state_id': []}}

    @api.onchange('state_id')
    def _onchange_state_id(self):
        id = self.country_id.search([('code', '=', self.state_id.code_provine)], limit=1).id
        self.country_id = id
    def is_number(self, s):
        regex = re.match(r'((0[1-9])+([0-9]{7,11})\b)', s)
        if regex is None:
            return False
        return True








