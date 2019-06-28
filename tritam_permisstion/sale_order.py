# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
from odoo.exceptions import AccessDenied, UserError
from odoo.exceptions import ValidationError
from lxml import etree
import re


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return super(SaleOrder, self)._read_group_stage_ids(stages, domain, order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self._context.get('search_default_partner_id', False):
            if domain:
                return super(SaleOrder, self).search_read(domain=[['partner_id', '=', self._context.get('search_default_partner_id', False)]], fields=fields, offset=offset,
                                                   limit=limit, order='create_date desc')
        if domain:
            name = domain[-1][2]
            if name and isinstance(name, str) and (len(name) >= 10\
                    and len(name) <= 13\
                    and self.is_number(name) is True\
                    and name.isdigit() is True\
                    and name == name.strip() or name[:1]=='*'):
                    domain = [u'|',u'|',[u'phone',u'=',domain[-1][2]],[u'mobile',u'=',domain[-1][2]],['partner_id.name','=',name[1:]]]
                    records = self.sudo().search(domain or [], offset=offset, limit=limit, order=order)
                    if not records:
                        return []

                    # if fields and fields == ['id']:
                    #     # shortcut read if we only want the ids
                    #     return [{'id': record.id} for record in records]
                    #
                    # # read() ignores active_test, but it would forward it to any downstream search call
                    # # (e.g. for x2m or function fields), and this is not the desired behavior, the flag
                    # # was presumably only meant for the main search().
                    # # TODO: Move this to read() directly?
                    # if 'active_test' in self._context:
                    #     context = dict(self._context)
                    #     del context['active_test']
                    #     records = records.with_context(context)
                    #
                    # result = records.read(fields)
                    # if len(result) <= 1:
                    #     return result
                    #
                    # # reorder read
                    # index = {vals['id']: vals for vals in result}
                    # return [index[record.id] for record in records if record.id in index]

                    index = [x.id for x in records]
                    return super(SaleOrder, self).search_read(domain=[['id', 'in', index]], fields=fields, offset=offset,
                                                  limit=limit, order='create_date desc')
        res = super(SaleOrder, self).search_read(domain=domain, fields=fields, offset=offset,
                                                  limit=limit, order=order)
        user_id = self.env.user.id
        if self.env.user.has_group('tritam_users.group_sales_team_manager'):
            domain += [['owner_id', '=', user_id]]
            res = super(SaleOrder, self).search_read(domain=domain, fields=fields, offset=offset,
                                                      limit=limit, order=order)
            return res
        if self.env.user.has_group('tritam_users.group_renew'):
            domain += [['owner_id', '=', user_id]]
            res = super(SaleOrder, self).search_read(domain=domain, fields=fields, offset=offset,
                                                      limit=limit, order=order)
            return res
        if self.env.user.has_group('tritam_users.group_renew') or self.env.user.has_group('tritam_users.group_sales_team_manager_group'):
                member = [user_id]
                for r in self.env['crm.team'].search([('user_id', '=', user_id)]):
                    [member.append(x) for x in r.member_ids.ids]
                domain += [['owner_id', 'in', member]]
                res = super(SaleOrder, self).search_read(domain=domain, fields=fields, offset=offset,
                                                          limit=limit, order=order)
                return res
        if self.env.user.has_group('tritam_users.group_renew_manager'):
                member = [user_id]
                for r in self.env['crm.team'].search([('user_id', '=', user_id)]):
                    [member.append(x) for x in r.member_ids.ids]
                domain += [['owner_id', 'in', member]]
                res = super(SaleOrder, self).search_read(domain=domain, fields=fields, offset=offset,
                                                          limit=limit, order=order)
                return res

        return res

    @api.multi
    def unlink(self):
        if not self.env.user.has_group('tritam_users.group_sales_admin') or not self.env.user.id != self.env.ref('base.user_root').id:
            raise ValidationError('The user do not have right to delete this record')
        else:
            return super(SaleOrder, self).unlink()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                   submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.env.user.id != self.env.ref('base.user_root').id:
            if self.env.user.has_group('tritam_users.group_nv_stock') or self.env.user.has_group('tritam_users.group_nv_check'):
                if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                    # and [some_condition]:
                    for node_form in doc.xpath("//kanban"):
                        node_form.set("create", 'false')
                    for node_form in doc.xpath("//tree"):
                        node_form.set("create", 'false')
                    for node_form in doc.xpath("//form"):
                        node_form.set("create", 'false')
            if view_type == 'form':
                if self.env.user.has_group('tritam_users.group_nv_stock') or self.env.user.has_group(
                        'tritam_users.group_nv_check'):
                    for node in doc.xpath("//field[@name='partner_id']"):
                        node.set('modifiers', '{"readonly": true}')
                    for node in doc.xpath("//field[@name='owner_id']"):
                        node.set('modifiers', '{"readonly": true}')
                    for node in doc.xpath("//field[@name='order_line']"):
                        node.set('modifiers', '{"readonly": true}')

        # if view_type == 'form':
        #     for node in doc.xpath("//field[@name='order_line']"):
        #         node.set('readonly', 'True')


        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def write(self, vals):
        if self.env.user.id == self.env.ref('base.user_root').id:
            return super(SaleOrder, self).write(vals)
        if self.env.user.has_group('tritam_users.group_nv_stock') or self.env.user.has_group('tritam_users.group_nv_check'):
            if vals.get('partner_id') or vals.get('owner_id') or vals.get('order_line'):
                raise ValidationError('Không có quyền sửa bản ghi')
            return super(SaleOrder, self).write(vals)
        else:
            return super(SaleOrder, self).write(vals)

    @api.one
    def action_cancels(self):
        if self.env.user.id == self.env.ref('base.user_root').id:
            self.write({'state': 'cancel'})
        if self.state in ('draft', 'send'):
            if self.env.user.has_group('tritam_users.group_sales_team_manager') or self.env.user.has_group(
                    'tritam_users.group_renew') or \
                    self.env.user.has_group('tritam_users.group_renew') or self.env.user.has_group(
                'tritam_users.group_sales_team_manager_group') \
                    or self.env.user.has_group('tritam_users.group_renew_manager') or self.env.user.has_group(
                'tritam_users.group_sales_admin') or self.env.user.has_group('tritam_users.group_nv_stock'):
                self.write({'state': 'cancel'})
            else:
                raise ValidationError('Không có quyền hủy đơn hàng')
        if self.state == 'sale':
            if self.env.user.has_group('tritam_users.group_nv_stock'):
                self.write({'state': 'cancel'})
            else:
                raise ValidationError('Không có quyền hủy đơn hàng')

    def is_number(self, s):
        regex = re.match(r'((0[1-9])+([0-9]{7,11})\b)', s)
        if regex is None:
            return False
        return True


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                     submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.env.user.id != self.env.ref('base.user_root').id:
            if view_type == 'form' or view_type == 'tree':
                if self.env.user.has_group('tritam_users.group_renew') or self.env.user.has_group('tritam_users.group_sales_team_manager')\
                        or self.env.user.has_group('tritam_users.group_sales_team_manager_group'):
                        for node_form in doc.xpath("//tree"):
                            node_form.set("create", 'false')
                        for node_form in doc.xpath("//tree"):
                            node_form.set("edit", 'false')
                        for node_form in doc.xpath("//form"):
                            node_form.set("create", 'false')
                        for node_form in doc.xpath("//form"):
                            node_form.set("edit", 'false')
                if self.env.user.has_group('tritam_users.group_renew_manager'):
                        for node_form in doc.xpath("//tree"):
                            node_form.set("create", 'false')
                        for node_form in doc.xpath("//tree"):
                            node_form.set("edit", 'false')
                        for node_form in doc.xpath("//form"):
                            node_form.set("create", 'false')
                        for node_form in doc.xpath("//form"):
                            node_form.set("edit", 'false')
        res['arch'] = etree.tostring(doc)
        return res

    # @api.multi
    # def action_cancel(self):
    #     if self.env.user.id != self.env.ref('base.user_root').id:
    #         if self.env.user.has_group('tritam_users.group_renew') or self.env.user.has_group('tritam_users.group_sales_team_manager')\
    #                 or self.env.user.has_group('tritam_users.group_sales_team_manager_group'):
    #             raise ValidationError('Không có quyền hủy DO')
    #         if self.env.user.has_group('tritam_users.group_renew_manager'):
    #             raise ValidationError('Không có quyền hủy DO')
    #     # self.mapped('move_lines').do_unreserve()
    #     return True