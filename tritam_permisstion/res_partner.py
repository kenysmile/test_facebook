# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
from odoo.exceptions import AccessDenied, UserError
from odoo.exceptions import ValidationError
from lxml import etree



class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset,
                                                  limit=limit, order=order)
        # context = self._context
        # if self.env.user.id == self.env.ref('base.user_root').id:
        #     return super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
        #                                                order=order)
        # else:
        if domain:
            name = domain[-1][2]
            #if name and isinstance(name, basestring) and ( len(name) >= 10 \
            if name and isinstance(name, str) \
                    and (len(name) >= 10 and len(name) <= 13 \
                    and self.is_number(name) is True \
                    and name.isdigit() is True \
                    and name == name.strip() or name[:1]=='*'):
                    domain = [u'|',u'|',[u'phone',u'=',domain[-1][2]],[u'mobile',u'=',domain[-1][2]],['name','=',name[1:]]]
                    records = self.search(domain or [], offset=offset, limit=limit, order=order)
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
        user_id = self.env.user.id
        if domain and domain[0][0] == 'id':
            return res
        # Kho Van
        if self.env.user.has_group('tritam_users.group_nv_stock'):
            domain += [['id', '=', 0]]
            res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)
            return res
        # --------------
        if self.env.user.has_group('tritam_users.group_sales_team_manager'):
            domain += [['id', 'in', list(set([x.partner_id.id for x in self.env['crm.lead'].search([('user_id', '=', user_id)])]))]]
            res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)
            return res
        if self.env.user.has_group('tritam_users.group_renew'):
            domain += [['id', 'in', list(set([x.partner_id.id for x in self.env['crm.lead'].search([('user_id', '=', user_id)])]))]]
            res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)
            return res
        if self.env.user.has_group('tritam_users.group_sales_team_manager_group') or self.env.user.has_group('tritam_users.group_renew_manager'):
            users_team = [user_id]
            for r in self.env['crm.team'].search([('user_id', '=', user_id)]):
                [users_team.append(x) for x in r.member_ids.ids]
            domain += [['id', 'in', list(set([x.partner_id.id for x in self.env['crm.lead'].search([('user_id', 'in', users_team)])]))]]
            res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)
            return res
        if self.env.user.has_group('tritam_users.group_sales_admin'):
            return res
        if self.env.user.has_group('tritam_users.group_contact'):
            domain += [['id', 'in', list(set([x.partner_id.id for x in self.env['crm.lead'].search([('user_id', '=', user_id)])]))]]
            res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)
            return res
        if self.env.user.has_group('tritam_users.group_nv_marketing'):
            domain += [['id', 'in', list(set([x.partner_id.id for x in self.env['crm.lead'].search([('user_id', '=', user_id)])]))]]
            res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)
            return res
        return res




            # res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
            #                                                    order=order)
            # return res



    @api.multi
    def unlink(self):
        if self.env.user.has_group('tritam_users.group_sales_admin') or self.env.user.id == self.env.ref('base.user_root').id:
            return super(ResPartner, self).unlink()
        else:
            raise ValidationError('The user do not have right to delete this record')

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(ResPartner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                  submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     if self.env.user.id != self.env.ref('base.user_root').id:
    #         if  view_type == 'form':
    #             if self.env.user.has_group('tritam_users.group_renew')or self.env.user.has_group('tritam_users.group_sales_team_manager')\
    #                     or self.env.user.has_group('tritam_users.group_sales_team_manager_group'):
    #                 for node in doc.xpath("//field[@name='phone']"):
    #                     node.set('modifiers', '{"readonly": true}')
    #                 for node in doc.xpath("//field[@name='mobile']"):
    #                     node.set('modifiers', '{"readonly": true}')
    #                 for node in doc.xpath("//field[@name='source_customer']"):
    #                     node.set('modifiers', '{"readonly": true}')
    #             if self.env.user.has_group('tritam_users.group_renew_manager') or self.env.user.has_group('tritam_users.group_nv_marketing') \
    #                     or self.env.user.has_group('tritam_users.group_contact'):
    #                 for node in doc.xpath("//field[@name='phone']"):
    #                     node.set('modifiers', '{"readonly": true}')
    #                 for node in doc.xpath("//field[@name='mobile']"):
    #                     node.set('modifiers', '{"readonly": true}')
    #                 for node in doc.xpath("//field[@name='source_customer']"):
    #                     node.set('modifiers', '{"readonly": true}')
    #     res['arch'] = etree.tostring(doc)
    #     return res


    @api.multi
    def write(self, vals):
        if self.env.user.has_group('tritam_users.group_sales_team_manager') or \
                self.env.user.has_group('tritam_users.group_renew')or \
                self.env.user.has_group('tritam_users.group_contact') or \
                self.env.user.has_group('tritam_users.group_nv_marketing'):
            if vals.get('phone') or vals.get('mobile') or vals.get('source_customer'):
                if self._context.get('params', False):
                    raise ValidationError('Không có quyền sửa bản ghi')
            return super(ResPartner, self).write(vals)
        else:
            return super(ResPartner, self).write(vals)