# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
from odoo.exceptions import AccessDenied, UserError
from odoo.exceptions import ValidationError
from lxml import etree
import re
from odoo.tools import OrderedSet


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self._context.get('search_default_partner_id', False):
            if domain:
                partner = self.env['res.users'].browse(self._context.get('search_default_partner_id', False))
                operator = '=' #'child_of' if partner.is_company else =
                # ids = self.env['crm.lead'].search([('partner_id', operator, partner.id), ('type', '=', 'opportunity')]).ids
                domain += [('partner_id', operator, partner.id)]
                return super(CrmLead, self).search_read(domain=domain, fields=fields, offset=offset,
                                                   limit=limit, order=order)
        if domain:
            name = str(domain[-1][2])
            #if name and isinstance(name, basestring) and  (len(name) >= 10 \
            if name and isinstance(name, str) and (len(name) >= 10 \
                                                          and len(name) <= 13 \
                    and self.is_number(name) is True \
                    and name.isdigit() is True \
                    and name == name.strip() or name[:1]=='*'):
                    domain = [u'|',u'|',[u'partner_id.phone',u'=',domain[-1][2]],[u'partner_id.mobile',u'=',domain[-1][2]],['partner_id.name','=',name[1:]]]
                    records = self.sudo().search(domain or [], offset=offset, limit=limit, order=order)
                    if not records:
                        return []

                    if fields and fields == ['id']:
                        # shortcut read if we only want the ids
                        return [{'id': record.id} for record in records]

                    # read() ignores active_test, but it would forward it to any downstream search call
                    # (e.g. for x2m or function fields), and this is not the desired behavior, the flag
                    # was presumably only meant for the main search().
                    # TODO: Move this to read() directly?
                    if 'active_test' in self._context:
                        context = dict(self._context)
                        del context['active_test']
                        records = records.with_context(context)

                    result = records.read(fields)
                    if len(result) <= 1:
                        return result

                    # reorder read
                    index = {vals['id']: vals for vals in result}
                    return [index[record.id] for record in records if record.id in index]
        res = super(CrmLead, self).search_read(domain=domain, fields=fields, offset=offset,
                                               limit=limit, order=order)
        if self.env.user.id == self.env.ref('base.user_root').id:
            return res
        user_id = self.env.user.id
        # Kho Van
        if self.env.user.has_group('tritam_users.group_nv_stock'):
            domain += [['user_id', '=', user_id]]
            res = super(CrmLead, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)
            return res

        # Telesale
        if self.env.user.has_group('tritam_users.group_sales_team_manager'):
            domain += [['user_id', '=', user_id]]
            # domain += [['probability', '!=', 0]]
            domain += [['active', '!=', False]]
            res = super(CrmLead, self).search_read(domain=domain, fields=fields, offset=offset,
                                                      limit=limit, order=order)
            return res
#         # Tai ki
        if self.env.user.has_group('tritam_users.group_renew'):
                    domain += [['user_id', '=', user_id]]
                    res = super(CrmLead, self).search_read(domain=domain, fields=fields, offset=offset,
                                                              limit=limit, order=order)
                    return res
        if self.env.user.has_group('tritam_users.group_sales_team_manager_group'):
                    member = [user_id]
                    for r in self.env['crm.team'].search([('user_id', '=', user_id)]):
                        [member.append(x) for x in r.member_ids.ids]
                    domain += [['user_id', 'in', member],['active', '!=', False]]
                    res = super(CrmLead, self).search_read(domain=domain, fields=fields, offset=offset,
                                                              limit=limit, order=order)
                    return res
        if self.env.user.has_group('tritam_users.group_renew_manager'):
                    member = [user_id]
                    for r in self.env['crm.team'].search([('user_id', '=', user_id)]):
                        [member.append(x) for x in r.member_ids.ids]
                    domain += [['user_id', 'in', member]]
                    res = super(CrmLead, self).search_read(domain=domain, fields=fields, offset=offset,
                                                              limit=limit, order=order)
                    return res

        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if domain:
            name = str(domain[-1][2])
            if name[:1]=='*':
                domain = [['partner_id.name','=',name[1:]]]
                result = self.sudo()._read_group_raw(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby,
                                              lazy=lazy)
                #groupby = [groupby] if isinstance(groupby, basestring) else list(OrderedSet(groupby))
                groupby = [groupby] if isinstance(groupby,
                                                  str) else list(
                    OrderedSet(groupby))
                dt = [
                    f for f in groupby
                    if self.sudo()._fields[f.split(':')[0]].type in ('date', 'datetime')
                ]
                for group in result:
                    for df in dt:
                        if group.get(df):
                            group[df] = group[df][1]
                return result
        return super(CrmLead, self).read_group(domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True)

    @api.multi
    def unlink(self):
        if self.env.user.has_group('tritam_users.group_sales_admin') or self.env.user.id == self.env.ref('base.user_root').id:
            return super(CrmLead, self).unlink()
        else:
            raise ValidationError('The user do not have right to delete this record')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CrmLead, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        # if self.env.user.has_group('tritam_users.group_sales_team_manager') or \
        #         self.env.user.has_group('tritam_users.group_sales_team_manager') or \
        #         self.env.user.has_group('tritam_users.group_sales_team_manager_group') or \
        #         self.env.user.has_group('tritam_users.group_renew_manager'):
        #     if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
        #         # and [some_condition]:
        #         for node_form in doc.xpath("//kanban"):
        #             node_form.set("create", 'false')
        #         for node_form in doc.xpath("//tree"):
        #             node_form.set("create", 'false')
        #         for node_form in doc.xpath("//form"):
        #             node_form.set("create", 'false')

        if self.env.user.id == self.env.ref('base.user_root').id:
            res['arch'] = etree.tostring(doc)
            return res
        else:
            if not self.env.user.has_group('tritam_users.group_sales_admin'):
                if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                    for node_form in doc.xpath("//kanban"):
                        node_form.set("create", 'false')
                    for node_form in doc.xpath("//tree"):
                        node_form.set("create", 'false')
                    for node_form in doc.xpath("//form"):
                        node_form.set("create", 'false')
            if view_type == 'form':
                if self.env.user.has_group('tritam_users.group_renew') or self.env.user.has_group('tritam_users.group_sales_team_manager'):
                        for node in doc.xpath("//field[@name='partner_id']"):
                            node.set('modifiers', '{"readonly": true}')
                if self.env.user.has_group('tritam_users.group_sales_team_manager_group'):
                        for node in doc.xpath("//field[@name='partner_id']"):
                            node.set('modifiers', '{"readonly": true}')
                        # for node in doc.xpath("//field[@name='user_id']"):
                        #     node.set('modifiers', '{"readonly": true}')

        res['arch'] = etree.tostring(doc)
        return res

    # @api.multi
    # def write(self, vals):
    #     if self.env.user.id == self.env.ref('base.user_root').id:
    #         return super(CrmLead, self).write(vals)
    #     if self.env.user.has_group('tritam_users.group_sales_team_manager') or \
    #             self.env.user.has_group('tritam_users.group_renew') or \
    #             self.env.user.has_group('tritam_users.group_sales_team_manager_group') or \
    #             self.env.user.has_group('tritam_users.group_renew_manager'):
    #         if vals.get('partner_id') or vals.get('user_id') or vals.get('source_customer'):
    #             raise ValidationError('Không có quyền sửa bản ghi')
    #         return super(CrmLead, self).write(vals)
    #     else:
    #         return super(CrmLead, self).write(vals)

    def is_number(self, s):
        regex = re.match(r'((0[1-9])+([0-9]{7,11})\b)', s)
        if regex is None:
            return False
        return True


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrExpense, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                   submenu=submenu)
        doc = etree.XML(res['arch'])
        if not self.env.user.has_group('tritam_users.group_nv_marketing'):
            if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                # and [some_condition]:
                for node_form in doc.xpath("//kanban"):
                    node_form.set("create", 'false')
                for node_form in doc.xpath("//tree"):
                    node_form.set("create", 'false')
                for node_form in doc.xpath("//form"):
                    node_form.set("create", 'false')
        res['arch'] = etree.tostring(doc)
        return res
