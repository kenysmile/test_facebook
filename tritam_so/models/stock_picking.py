# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
import sys
#reload(sys)
#sys.setdefaultencoding("utf8")

class tritam_stock_picking(models.Model):
    _inherit = 'stock.picking'

    # def add_months(self,sourcedate, months):
    #     month = sourcedate.month - 1 + months
    #     year = int(sourcedate.year + month / 12)
    #     month = month % 12 + 1
    #     day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    #     return date(year, month, day)
    do_shipping_id = fields.Char(string='Mã vận đơn',compute='_compute_do_shipping_id')
    do_request_date = fields.Date(string='Requested Date',readonly=True,compute='_compute_do_shipping_id')
    # do_schedule_date = fields.Date(string='Schedule Date',readonly=True,compute='_compute_do_shipping_id')
    do_shipping_fee = fields.Float(string='Phí ship',digits=0,readonly=True,compute='_compute_do_shipping_id')
    x_carrier_id = fields.Many2one("delivery.carrier", string="Nhà vận chuyển",readonly=True,compute='_compute_do_shipping_id')


    @api.multi
    @api.depends('group_id')
    def _compute_do_shipping_id(self):
        for rec in self:
            if rec.group_id:
                rec.do_shipping_id = rec.group_id.sale_id.shipping_id or ""
                rec.do_request_date = rec.group_id.sale_id.request_date or ""
                rec.x_carrier_id = rec.group_id.sale_id.carrier_id.id
                rec.do_shipping_fee = rec.group_id.sale_id.shipping_fee or 0


    @api.multi
    def do_new_transfer(self):

        obj_setting = self.env['tritam.sms'].sudo().search([], limit=1)
        # so = self.env['sale.order'].browse(self.group_id.procurement_ids[0].sale_line_id.order_id.id) \
        #      or self.env['sale.order'].search([('name','=',self.group_id.name)])
        if self.group_id:
            so = self.env['sale.order'].browse(self.group_id.sale_id.id)
        else:
            so = self.env['sale.order'].search([('name','=',self.group_id.name)])
        if self.name.find('RETURN') != -1:
            so.write({'x_status_do': 4,
                      'date_status_do': fields.Date.today()})
        if self.name.find('PICK') != -1:
           # so = self.env['sale.order'].browse(self.group_id.procurement_ids[0].sale_line_id.order_id.id)
           so.write({'x_status_do': 2,
                    'date_status_do' : fields.Date.today()})
           id_op = self.env['crm.stage'].search([('type_state','=',3)],limit = 1)
           if id_op:
                so.opportunity_id.write({'stage_id': id_op.id})
        if self.name.find('OUT') != -1:
           # so = self.env['sale.order'].browse(self.group_id.procurement_ids[0].sale_line_id.order_id.id)
           so.action_invoice_create(final=True)
           so.write({'x_status_do': 3,
                    'date_status_do' : fields.Date.today()})
           id_op = self.env['crm.stage'].search([('type_state','=',4)],limit = 1)
           if id_op:
                so.opportunity_id.write({'stage_id': id_op.id})
           obj_so_line = self.env['sale.order.line'].search([('order_id','=',self.group_id.sale_id.id)])
           product_name = ""
           if obj_so_line:
               for rec in obj_so_line :
                   time_use = rec.product_id.product_tmpl_id.usage_time * rec.product_uom_qty - rec.product_id.product_tmpl_id.recurring_date
                   # time_resign = self.add_months(fields.datetime.now(),int(time_use))
                   time_resign = fields.datetime.now()+timedelta(days=int(time_use))
                   rec.write({'start_date': fields.datetime.now().strftime('%Y-%m-%d'),
                              'end_date':time_resign.strftime('%Y-%m-%d')})
                   rec.order_partner_id.write({'detail_support_ids': [
                        (0, 0, {
                            'product_id': rec.product_id.id,
                            'order_id': self.group_id.sale_id.id,
                            'start_date': fields.datetime.now().strftime('%Y-%m-%d'),
                            'end_date': time_resign.strftime('%Y-%m-%d'),
                            })],
                       'to_support':'yes'})
                   product_name += rec.product_id.name+","
        res = super(tritam_stock_picking, self).button_validate()
        return res

    @api.multi
    def button_draft(self):
        for rec in self:
            if rec.state == 'done' or rec.state == 'confirmed' or rec.state == 'assigned' or rec.state == 'waiting':
                rec.state = 'draft'

    # @api.multi
    # def action_cancel(self):
    #     res = super(tritam_stock_picking, self).do_unreserve()
    #     if self.name.find('OUT') != -1:
    #        so = self.env['sale.order'].browse(self.group_id.procurement_ids[0].sale_line_id.order_id.id)
    #        so.write({'x_status_do': 7,
    #                 'date_status_do' : fields.Date.today()})
    #        id_op = self.env['crm.stage'].search([('type_state','=',5)],limit = 1)
    #        if id_op:
    #             so.opportunity_id.write({'stage_id': id_op.id})
    #     return res
    # @api.multi
    # def do_new_transfer(self):
    #     res = super(tritam_stock_picking, self).do_new_transfer()
    #     quantity_total = 0
    #     for i in self.move_lines:
    #         quantity_total += i.product_uom_qty
    #     if self.name.find('PICK') != -1 :
    #
    #         ########################pick#####################################
    #         pick_city_id = int(self.group_id.procurement_ids[0].sale_line_id.order_id.warehouse_id.partner_id.country_id.code)
    #         pick_district_id = int(self.group_id.procurement_ids[0].sale_line_id.order_id.warehouse_id.partner_id.state_id.code)
    #         pick_inventory_number = self.group_id.procurement_ids[0].sale_line_id.order_id.warehouse_id.name
    #         pick_ward_id = int(self.group_id.procurement_ids[0].sale_line_id.order_id.warehouse_id.partner_id.city.code_ward)
    #         pick_address = self.group_id.procurement_ids[0].sale_line_id.order_id.warehouse_id.partner_id.street
    #         pick_phone = self.group_id.procurement_ids[0].sale_line_id.order_id.warehouse_id.partner_id.phone or ""
    #         pick_fullname = self.group_id.procurement_ids[0].sale_line_id.order_id.warehouse_id.partner_id.name or ""
    #         ########################config######################################
    #         cf_service_code = 4
    #         cf_weight = int(self.weight_total)
    #         cf_amount = int(self.amount_total)
    #         cf_quantity = int(quantity_total)
    #         cf_collection = int(self.amount_total)
    #         cf_vas = ''
    #         cf_censorship = 1
    #         cf_payment = 1
    #         cf_type = "0"
    #         ###########################delivery##########################
    #         de_city_id = int(self.group_id.procurement_ids[0].sale_line_id.order_id.partner_id.country_id.code)
    #         de_district_id = int(self.group_id.procurement_ids[0].sale_line_id.order_id.partner_id.state_id.code)
    #         de_ward_id = int(self.group_id.procurement_ids[0].sale_line_id.order_id.partner_id.city.code_ward)
    #         de_address = self.group_id.procurement_ids[0].sale_line_id.order_id.partner_id.street
    #         de_phone = self.group_id.procurement_ids[0].sale_line_id.order_id.partner_id.phone or ""
    #         de_fullname = self.group_id.procurement_ids[0].sale_line_id.order_id.partner_id.name or ""
    #         ##########################parcel###########################
    #         parcel_items_weight = ""
    #         parcel_items_amount = ""
    #         parcel_items_quanlity = ""
    #         parcel_items_description = ""
    #         parcel_items_product_name = ""
    #         parcel_total_amount = ""
    #         parcel_total_weight = ""
    #         #########################################################
    #         sale_order_number = self.group_id.procurement_ids[0].sale_line_id.order_id.name
    #         # self.env['tritam.tracking'].create_order_vtp(pick_city_id, pick_district_id, pick_inventory_number, pick_ward_id, pick_address,
    #         #              pick_phone, pick_fullname, cf_service_code, cf_weight, cf_amount, cf_quantity, cf_collection,
    #         #              cf_vas, cf_censorship, cf_payment, cf_type, de_city_id, de_district_id, de_ward_id, de_address,
    #         #              de_phone, de_fullname, parcel_items_weight, parcel_items_amount, parcel_items_quanlity,
    #         #              parcel_items_description, parcel_items_product_name, parcel_total_amount, parcel_total_weight,sale_order_number)
    #     return res

class AccountInvoiceinherir(models.Model):
    _inherit = "account.invoice"

    ai_shipping_id = fields.Char(string='Mã vận đơn', readonly=True,compute='_compute_do_shipping_id')
    ai_request_date = fields.Date(string='Requested Date',readonly=True,compute='_compute_do_shipping_id')
    # ai_schedule_date = fields.Date(string='Schedule Date',readonly=True,compute='_compute_do_shipping_id')
    ai_shipping_fee = fields.Float(string='Phí ship',digits=0,readonly=True,compute='_compute_do_shipping_id')
    carrier_id = fields.Many2one("delivery.carrier", string="Phương án ship hàng ",readonly=True,compute='_compute_do_shipping_id')


    @api.multi
    @api.depends('origin')
    def _compute_do_shipping_id(self):
        for rec in self :
            obj = self.env['sale.order'].search([('name','=',rec.origin)],limit=1)
            if obj :
                rec.ai_shipping_id = obj.shipping_id
                rec.ai_request_date = obj.request_date
                # rec.ai_schedule_date = obj.schedule_date
                rec.ai_shipping_fee = obj.shipping_fee
                rec.carrier_id = obj.carrier_id.id

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoiceinherir, self).action_invoice_open()
        so_obj = self.env['sale.order'].search([('name','=',self.origin)],limit=1)
        so_obj.write({'x_status_invoice': "Đã đối soát doanh thu, "
                                 "" + "("+fields.datetime.now().strftime('%d/%m/%Y %H:%M:%S')+","
                                   +str(self.env['res.users'].browse(self._uid).name)+")"})
        return res

class account_payment_inherit(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        res = super(account_payment_inherit, self).post()
        if self.env.context.get('active_id'):
            ai_obj = self.env['account.invoice'].browse(self.env.context.get('active_id'))
            if self.env['account.invoice'].browse(self.env.context.get('active_id')).origin:
                so_obj = self.env['sale.order'].search([('name','=',self.env['account.invoice'].browse(self.env.context.get('active_id')).origin)],limit=1)
                so_obj.write({'x_status_invoice': "Doanh thu đã chuyển về tài khoản"})
        return res

# class StockImmediateTransfer(models.TransientModel):
#     _inherit = 'stock.immediate.transfer'

    # @api.multi
    # def process(self):
    #     self.ensure_one()
    #     # If still in draft => confirm and assign
    #     if self.pick_id.state == 'draft':
    #         self.pick_id.action_confirm()
    #         if self.pick_id.state != 'assigned':
    #             self.pick_id.action_assign()
    #             if self.pick_id.state != 'assigned':
    #                 raise UserError(_(
    #                     "Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
    #     for pack in self.pick_id.pack_operation_ids:
    #         if pack.product_qty > 0:
    #             pack.write({'qty_done': pack.product_qty})
    #         else:
    #             pack.unlink()
    #     if self.pick_id.partner_id:
    #         self.pick_id.partner_id.level = 6
    #     self.pick_id.do_transfer()

    class StockImmediateTransfer(models.TransientModel):
        _name = 'stock.immediate.transfer'
        _description = 'Immediate Transfer'

        pick_ids = fields.Many2many('stock.picking',
                                     'stock_picking_transfer_rel')

        def process(self):
            pick_to_backorder = self.env['stock.picking']
            pick_to_do = self.env['stock.picking']

            for picking in self.pick_ids:
                # If still in draft => confirm and assign
                if picking.state == 'draft':
                    picking.action_confirm()
                    if picking.state != 'assigned':
                        picking.action_assign()
                        if picking.state != 'assigned':
                            raise UserError(_(
                                "Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                for move in picking.move_lines.filtered(
                        lambda m: m.state not in ['done', 'cancel']):
                    for move_line in move.move_line_ids:
                        # print('xxxxxxxxxx')
                        move_line.qty_done = move_line.product_uom_qty
                        move_line.quantity_done = move_line.product_uom_qty
                        move_line.write({'quantity_done': move_line.product_uom_qty})
                if picking._check_backorder():
                    pick_to_backorder |= picking
                    continue
                pick_to_do |= picking
            # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
            if pick_to_do:
                for pick_id_1 in pick_to_do:
                    if pick_id_1:
                        pick_id_1.partner_id.level = 6
                #self.picking.partner_id.level = 6
                pick_to_do.action_done()
            if pick_to_backorder:
                return pick_to_backorder.action_generate_backorder_wizard()
            return False


            # return self.pick_id.do_transfer()

# class ReturnPickingInherit(models.TransientModel):
#     _inherit = 'stock.return.picking'
#     # overide base edit mes exception validate Stock Picking Return
#     @api.multi
#     def _create_returns(self):
#         # TDE FIXME: store it in the wizard, stupid
#         picking = self.env['stock.picking'].browse(self.env.context['active_id'])
#
#         return_moves = self.product_return_moves.mapped('move_id')
#         unreserve_moves = self.env['stock.move']
#         for move in return_moves:
#             to_check_moves = self.env['stock.move'] | move.move_dest_id
#             while to_check_moves:
#                 current_move = to_check_moves[-1]
#                 to_check_moves = to_check_moves[:-1]
#                 if current_move.state not in ('done', 'cancel') and current_move.reserved_quant_ids:
#                     unreserve_moves |= current_move
#                 split_move_ids = self.env['stock.move'].search([('split_from', '=', current_move.id)])
#                 to_check_moves |= split_move_ids
#
#         if unreserve_moves:
#             unreserve_moves.do_unreserve()
#             # break the link between moves in order to be able to fix them later if needed
#             unreserve_moves.write({'move_orig_ids': False})
#
#         # create new picking for returned products
#         picking_type_id = picking.picking_type_id.return_picking_type_id.id or picking.picking_type_id.id
#         new_picking = picking.copy({
#             'move_lines': [],
#             'picking_type_id': picking_type_id,
#             'state': 'draft',
#             'origin': picking.name,
#             'location_id': picking.location_dest_id.id,
#             'location_dest_id': self.location_id.id})
#         new_picking.message_post_with_view('mail.message_origin_link',
#             values={'self': new_picking, 'origin': picking},
#             subtype_id=self.env.ref('mail.mt_note').id)
#
#         returned_lines = 0
#         for return_line in self.product_return_moves:
#             if not return_line.move_id:
#                 raise UserError(_("You have manually created product lines, please delete them to proceed"))
#             new_qty = return_line.quantity
#             if new_qty:
#                 # The return of a return should be linked with the original's destination move if it was not cancelled
#                 if return_line.move_id.origin_returned_move_id.move_dest_id.id and return_line.move_id.origin_returned_move_id.move_dest_id.state != 'cancel':
#                     move_dest_id = return_line.move_id.origin_returned_move_id.move_dest_id.id
#                 else:
#                     move_dest_id = False
#
#                 returned_lines += 1
#                 return_line.move_id.copy({
#                     'product_id': return_line.product_id.id,
#                     'product_uom_qty': new_qty,
#                     'picking_id': new_picking.id,
#                     'state': 'draft',
#                     'location_id': return_line.move_id.location_dest_id.id,
#                     'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
#                     'picking_type_id': picking_type_id,
#                     'warehouse_id': picking.picking_type_id.warehouse_id.id,
#                     'origin_returned_move_id': return_line.move_id.id,
#                     'procure_method': 'make_to_stock',
#                     'move_dest_id': move_dest_id,
#                 })
#
#         if not returned_lines:
#             str = _("Please specify at least one non-zero quantity.(%s) "%(picking.group_id.procurement_ids[0].sale_line_id.order_id.name))
#             raise UserError(str)
#
#         new_picking.action_confirm()
#         new_picking.action_assign()
#         return new_picking.id, picking_type_id
