# -*- coding: utf-8 -*-
from odoo import models,fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import datetime
import re



# class SaleConfiguration(models.TransientModel):
#     _inherit = 'sale.config.settings'
#
#     number_use = fields.Integer(string="Số lần tái sử dụng *")
#
#     @api.model
#     def get_number_use_setting(self, fields):
#         return {
#             'number_use': 0 if self.env['ir.values'].get_defaults_dict('sale.config.settings').get(
#                 'number_use') == 'fixed' else 1
#             }
#
#     @api.model
#     def set_number_use_settings(self):
#         return self.env['ir.values'].sudo().set_default(
#             'sale.config.settings', 'number_use', self.number_use)
class UpdateDelivery(models.Model):
    _inherit = 'delivery.carrier'

    product_id = fields.Many2one('product.product', string='Delivery Product',
                                 required=False, ondelete='restrict')



class tritam_sale_order(models.Model):
    _inherit = 'sale.order'
    _sql_constraints = [('shipping_id', 'unique(shipping_id)', 'Mã vận đơn này đã tồn tại'),
                        ('shipping_id_return_check', 'unique(shipping_id_return)', 'Mã vận đơn hoàn này đã tồn tại')]


    date_cancel = fields.Date(string='Cancel quotation')
    request_date = fields.Date(string='Requested Date')
    date_transfer = fields.Date(string='Validate Deliver Order Stock/Output')
    date_done =fields.Date(string='Validate Delivery Order Output/Customer')
    date_return = fields.Date(string='Date Return')
    owner_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Owner state')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Đơn hàng xác nhận'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    # x_status_do = fields.Char(string="Trạng thái vận chuyển",default="Chưa xác nhận", readonly=True)
    x_status_do = fields.Selection([
        (1, 'Chưa chuyển cho giao vận'),
        (2, 'Đơn hàng đang đi đường'),
        (3, 'Đơn hàng hoàn thành'),
        (4, 'Đã nhập kho hoàn'),
        (7, 'Đơn hoàn'),
        ], string='Trạng thái vận chuyển',default=1,readonly=False)
    date_status_do = fields.Date(string='Ngày thực hiện vận chuyển')
    x_status_invoice = fields.Char(string="Đối soát doanh thu",default="Chưa đối soát doanh thu", readonly=True)
    so_team_marketing = fields.Many2one('hr.department', related='partner_id.team_marketing', string='Team Marketing', readonly=True)
    so_source_customer = fields.Many2one('customer.source', related='partner_id.source_customer', string='Nguồn', readonly=True)
    so_type_contact = fields.Selection(related='opportunity_id.type_contact',readonly=True)
    schedule_date = fields.Date(string='Schedule Date',invisible=True)
    shipping_fee = fields.Float(string='Phí ship',digits=0)
    shipping_id = fields.Char(compute='_compute_name_reference', string='Mã vận đơn')
    shipping_fee_return = fields.Float(string='Phí ship đơn hoàn',digits=0)
    shipping_id_return = fields.Char(string='Mã vận đơn hoàn')

    # end_date_max = fields.Date(compute='_compute_end_date_max', string='Ngày TK sau', store=True)
    # end_date_min = fields.Date(compute='_compute_end_date_min', string='Ngày TK trước', store=True)
    #
    # start_date_min = fields.Date(compute='_compute_start_date_min',
    #                            string='Ngày CS trước', store=True)

    so_pn_2 = fields.Integer(related='partner_id.sale_order_count', store=True, string='Số đơn hàng', compute='_compute_sum_so_2')


    # fields trong base (source_id)
    source_id = fields.Many2one('utm.source', string='Source',related='partner_id.utm_id',
                                help="This is the link source, e.g. Search Engine, another domain,or name of email list")
    x_check_viettel = fields.Selection([
        (1, 'Đã đối soát phí cước'),
        (2, 'Chưa đối soát phí cước'),
        (3, 'Đã đối soát phí cước đơn hoàn'),
    ], string='Đối soát phí cước', default= 2)
    internal_reference = fields.Char(string='Internal Reference',compute='_compute_internal_reference')
    sum_qty = fields.Integer('Sum Qty Line',compute='_compute_internal_reference')

    @api.depends('state')
    def _compute_name_reference(self):
        for rec in self:
            if rec.name and rec.state == "sale":
                rec.shipping_id = rec.name

    @api.multi
    @api.depends('order_line')
    def _compute_internal_reference(self):
        for rec in self :
            arr_lines=[]
            sum_qty = 0
            if rec.order_line:
                for line in rec.order_line:
                    default_code = line.product_id.default_code or "Sản phẩm không setting internal reference "
                    value = str(int(line.product_uom_qty))+" "+default_code
                    arr_lines.append(value)
                    sum_qty +=line.product_uom_qty
                rec.internal_reference = str("+".join(arr_lines))
                rec.sum_qty = sum_qty
    @api.multi
    def action_cancel(self):
        if self.partner_id:
            self.partner_id.level = 5
        self.write({'state': 'cancel'})
        self.write({'date_cancel': datetime.datetime.today().date()})
        if self.opportunity_id:
           id_op = self.env['crm.stage'].search([('type_state','=',1)],limit = 1)
           if id_op:
            self.opportunity_id.write({'stage_id': id_op.id})

    @api.multi
    def action_confirm(self):
        res = super(tritam_sale_order, self).action_confirm()
        for order in self:
            if order.partner_id:
                order.partner_id.level = 4
        if self.picking_ids:
            for r in self.picking_ids:
                r.amount_total = self.amount_total
        if self.opportunity_id:
           id_op = self.env['crm.stage'].search([('type_state','=',2)],limit = 1)
           if id_op:
            self.opportunity_id.write({'stage_id': id_op.id})
        product_name =""
        if self.order_line:
            for r in self.order_line:
                product_name += r.product_id.name+","
        # obj_setting = self.env['tritam.sms'].sudo().search([], limit=1)
        # sms_do_confirmsale = False
        # if obj_setting :
        #     sms_do_confirmsale = obj_setting[0].sms_do_confirmsale
        # if sms_do_confirmsale:
        #     content = re.sub(r'<.*?>', '', self.env.ref('tritam_cpn_api.mail_template_sms_api_sale').body_html).replace('\n', '')
        #     content_cv = content.format(donhang= self.name,contact=self.partner_id.name,diachi=self.partner_id.street or "",sanpham=product_name,ngayxacnhan =self.confirmation_date)
        #     if self.partner_id.phone:
        #         self.env['tritam.sms'].send_sms_api(self.partner_id.phone, content_cv)
        #     else:
        #         raise UserError(_("Khách hàng chưa có số điện thoại để gửi tin nhắn"))
        return res

    @api.model
    def create(self, vals):
        if 'opportunity_id' in vals:
            leads = self.env['crm.lead'].browse(vals['opportunity_id'])
            leads.action_set_won()
        if 'partner_id' in vals :
            obj_parner = self.env['res.partner'].browse([vals['partner_id']])
            if obj_parner.street is False or obj_parner.state_id.id is False or obj_parner.country_id.id is False:
                raise UserError(_("Bạn cần điền đầy đủ số nhà, quận huyện, tỉnh thành thì mới tạo được đơn hàng"))
        if 'order_line' in vals and not vals['order_line']:
            raise UserError(_("Bạn cần nhập order line trước khi tạo sale order"))
        return super(tritam_sale_order, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'partner_id' in vals :
            obj_parner = self.env['res.partner'].browse([vals['partner_id']])
            if obj_parner.street is False or obj_parner.state_id.id is False or obj_parner.country_id.id is False:
                raise UserError(_("Bạn cần điền đầy đủ số nhà, quận huyện, tỉnh thành thì mới tạo được đơn hàng"))
        if 'order_line' in vals and vals['order_line'][0] and len(
                vals['order_line']) < 2 and not vals['order_line'][0][2]:
            raise UserError(_("Bạn cần có ít nhất một order line"))
        return super(tritam_sale_order, self).write(vals)
    # @api.one
    # def sent_by_sms(self):
    #     content = re.sub(r'<.*?>', '', self.env.ref('tritam_cpn_api.mail_template_sms_api_sale_miss_call').body_html).replace('\n', '')
    #     content_cv = content.format(contact=self.partner_id.name)
    #     if self.partner_id.phone:
    #         self.env['tritam.sms'].send_sms_api(self.partner_id.phone, content_cv)
    #     else:
    #         raise UserError(_("Khách hàng chưa có số điện thoại để gửi tin nhắn"))
    #     # self.write({'state': 'sent'})
    #     return True

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is %s no invoicable line.'%(self.name)))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is %s no invoicable line.' % (self.name)))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]

class tri_tam_sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    # _rec_name = 'end_date'date
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    x_discount = fields.Float('Giảm Giá')
    x_unit_price = fields.Float('Đơn giá',readonly=True, compute='_compute_x_unit_price',groups='tritam_users.group_sales_team_manager')


    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        if self.product_uom_qty < 1 :
            raise UserError(_("Trường sản phẩm không được để trống và phải có số lượng lớn hơn 0"))

    @api.multi
    @api.depends('price_unit')
    def _compute_x_unit_price(self):
        for rec in self :
            rec.x_unit_price = rec.price_unit

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','x_discount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'] - line.x_discount,
            })
    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'x_discount': self.x_discount,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            # 'account_analytic_id': self.order_id.project_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    weight_total =  fields.Float(string='Trọng lượng')
    amount_total = fields.Float(string='Tổng tiền cần thanh toán')
    amount_compute = fields.Float(compute='def_compute')
    street = fields.Char(string="Address", related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    # ward_id = fields.Many2one('tritam.tracking.location.ward', related='partner_id.city')
    state_id = fields.Many2one('res.country.state', related='partner_id.state_id')
    country_id = fields.Many2one('res.country', related='partner_id.country_id')


