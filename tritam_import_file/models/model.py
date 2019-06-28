# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools,_
import xlrd, base64
from odoo.osv import osv


class tritam_import_file(models.TransientModel):
    _name = "tritam.import.file"

    name = fields.Char('Message')
    file_import = fields.Binary(string="Upload File")
    file_import_name = fields.Char()
    tab_cod = fields.Selection([
        # (1, 'Đối soát phí cước'),
        (1, 'Import Mã vận đơn thường'),
        (2, 'Import Mã vận đơn hoàn'),
        (3, 'Update Trạng Thái Vận Chuyển')
    ], string='Loại import')
    tab_cod_check = fields.Selection([
        # (1, 'Đối soát phí cước'),
        (1, 'Ghi nhận cước đơn thường'),
        (2, 'Ghi nhận cước đơn hoàn'),
        (3, 'Đối soát COD'),
        (4, 'Xác nhận đã nhận tiền COD'),
        (5, 'Xác nhận đã thanh toán cước')
    ], string='Loại import')
    invoice_date = fields.Date('Invoice Date')
    journal_id = fields.Many2one('account.journal', string='Journal',domain =[('at_least_one_inbound', '=', True), ('type', 'in', ('bank', 'cash'))])

    @api.multi
    def check_doi_soat_tab_check(self):
        if self.tab_cod_check == 1 :
            self.import_shipping_fee_money()
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('tritam_import_file.custom_pop_message_wizard_view_form').id,
                'res_model': 'tritam.import.file',
                'target': 'new',
                'context': {'default_name': "Hệ thống đã import thành công cước đơn thường."}
            }
        if  self.tab_cod_check == 2 :
            self.import_shipping_fee_money_return()
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('tritam_import_file.custom_pop_message_wizard_view_form').id,
                'res_model': 'tritam.import.file',
                'target': 'new',
                'context': {'default_name': "Hệ thống đã import thành công cước đơn hoàn."}
            }
        if  self.tab_cod_check == 3 :
            self.save_file_tab_cod()
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('tritam_import_file.custom_pop_message_wizard_view_form').id,
                'res_model': 'tritam.import.file',
                'target': 'new',
                'context': {'default_name': "Hệ thống đối soát thành công COD."}
            }
        if  self.tab_cod_check == 4 :
            self.tab_cod_register_payment()
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('tritam_import_file.custom_pop_message_wizard_view_form').id,
                'res_model': 'tritam.import.file',
                'target': 'new',
                'context': {'default_name': "Hệ thống xác nhận tiền COD thành công."}
            }
        if  self.tab_cod_check == 5 :
            self.import_create_new_expense()
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('tritam_import_file.custom_pop_message_wizard_view_form').id,
                'res_model': 'tritam.import.file',
                'target': 'new',
                'context': {'default_name': "Hệ thống xác nhận thanh toán cước vận chuyển thành công."}
            }

    @api.multi
    def check_doi_soat_tab(self):
        # if  self.tab_cod == 1 :
        #     self.save_file()
        # if self.tab_cod == 2 :
        #     self.save_file_tab_cod()
        if self.tab_cod == 1 :
            self.import_shipping_fee()
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('tritam_import_file.custom_pop_message_wizard_view_form').id,
                'res_model': 'tritam.import.file',
                'target': 'new',
                'context': {'default_name': "Hệ thống đã import thành công mã vận đơn."}
            }
        elif self.tab_cod == 2 :
            self.import_shipping_fee_return()
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('tritam_import_file.custom_pop_message_wizard_view_form').id,
                'res_model': 'tritam.import.file',
                'target': 'new',
                'context': {'default_name': "Hệ thống đã import thành công mã vận đơn hoàn."}
            }
        elif self.tab_cod == 3 :
            self.import_update_do()
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('tritam_import_file.custom_pop_message_wizard_view_form').id,
                'res_model': 'tritam.import.file',
                'target': 'new',
                'context': {'default_name': "Hệ thống đã cập nhật thành công trạng thái vận chuyển."}
            }

    @api.multi
    def import_create_new_expense(self, context=None):
        # kiểm tra file có rỗng
        if self.file_import is None:
            raise osv.except_orm('Error', 'File is not empty')
        # Kiểm tra định dạng file
        self.check_format_file_excel(self.file_import_name)
        # tiến hành đọc file
        file_import = self.file_import
        data = base64.decodestring(file_import)
        excel = xlrd.open_workbook(file_contents=data)
        sheet = excel.sheet_by_index(0)
        excep_so = []
        excep_so_return = []
        excep_exspen = []
        try:
            index = 1
            index_return = 1
            so_obj = self.env['sale.order']
            total_shipping = 0
            total_shipping_return = 0
            while index < sheet.nrows:
                shipping_id = sheet.cell(index, 0).value
                shipping_id_money = sheet.cell(index, 1).value
                if shipping_id == "" or shipping_id_money == "":
                    index = index + 1
                    continue
                if self.is_number(shipping_id_money) == False:
                    message = "Số tiền không thể là chữ: " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                if self.is_number(shipping_id) == True:
                    shipping_id = str(int(shipping_id))
                sale_order = so_obj.search([('shipping_id', '=', shipping_id)],limit = 1)
                if sale_order :
                    if sale_order.shipping_fee == shipping_id_money:
                        total_shipping +=shipping_id_money
                    else:
                        excep_exspen.append(sale_order.name)
                else:
                    excep_so.append(shipping_id)
                index = index + 1
            if excep_exspen:
                message = "Tiền của mã SO không khớp: " + str(",".join(excep_exspen))
                raise osv.except_osv("Cảnh báo !", message)
            if excep_so:
                message = "Không tìm thấy mã vận đơn : " + str(",".join(excep_so))
                raise osv.except_osv("Cảnh báo !", message)
            while index_return < sheet.nrows:
                shipping_id_return = sheet.cell(index_return, 2).value
                shipping_id_money_return = sheet.cell(index_return, 3).value
                if shipping_id_return == "" or shipping_id_money_return == "":
                    index_return = index_return + 1
                    continue
                if self.is_number(shipping_id_money_return) == False:
                    message = "Số tiền không thể là chữ: " + str(index_return + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                if self.is_number(shipping_id_return) == True:
                    shipping_id_return = str(int(shipping_id_return))
                sale_order_return = so_obj.search([('shipping_id_return', '=', shipping_id_return),('shipping_fee_return','=',shipping_id_money_return)],limit = 1)

                if sale_order_return :
                    total_shipping_return +=shipping_id_money_return
                else :
                    excep_so_return.append(shipping_id_return)
                index_return = index_return + 1
            if excep_so_return:
                message = "Không tìm thấy mã vận đơn hoàn : " + str(",".join(excep_so_return))
                raise osv.except_osv("Cảnh báo !", message)
            total = total_shipping_return+total_shipping
            product = self.env['product.product'].search([('can_be_expensed', '=', True)], limit=1)
            employ = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if product and employ :
                create = self.env['hr.expense'].sudo().create({
                    'name': product.name,
                    'product_id': product.id,
                    'unit_amount': total,
                    'employee_id': employ.id,
                    'date':self.invoice_date,
                    'payment_mode': "company_account"
                })
                create_sheet = self.env['hr.expense.sheet'].sudo().create({
                    'name': create.name,
                    'employee_id': create.employee_id.id,
                    'bank_journal_id':self.journal_id.id,
                    'expense_line_ids': [(4, create.id, 0)]
                })
                create_sheet.approve_expense_sheets()
                create_sheet.action_sheet_move_create()
            else:
                message = _("Không có sản phẩm phí ship hoặc user này không phải là employee")
                raise osv.except_osv("Cảnh báo !", message)
            self.file_import = None
        except IndexError:
            raise osv.except_orm("Error", "Thiếu cột dữ liệu")

    @api.multi
    def tab_cod_register_payment(self, context=None):
        # kiểm tra file có rỗng
        if self.file_import is None:
            raise osv.except_orm('Error', 'File is not empty')
        # Kiểm tra định dạng file
        self.check_format_file_excel(self.file_import_name)
        # tiến hành đọc file
        file_import = self.file_import
        data = base64.decodestring(file_import)
        excel = xlrd.open_workbook(file_contents=data)
        sheet = excel.sheet_by_index(0)
        try:
            index = 1
            so_obj = self.env['sale.order']
            ai_obj = self.env['account.invoice']
            payment_model = self.env['account.payment']
            excep_so = []
            ex_ai =[]
            while index < sheet.nrows:
                code_transfer = sheet.cell(index, 0).value
                money = sheet.cell(index, 1).value or 0
                if self.is_number(code_transfer) == True:
                    code_transfer = str(int(code_transfer))
                if self.is_number(money) == False:
                    message = "Số tiền không thể là chữ: " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                name_so = so_obj.search([('shipping_id', '=', code_transfer),('amount_total','=',money)],limit = 1)
                if name_so :
                    account_invoice = ai_obj.search([('origin', '=', name_so.name),('state', '=', 'open')])
                    if account_invoice:
                        for rec in account_invoice:
                            post_fixed = {
                                'journal_id': self.journal_id.id,
                                'payment_method_id': 1,
                                'payment_date': self.invoice_date,
                                'communication': rec.number,
                                'invoice_ids': [(4, rec.id, None)],
                                'payment_type': 'inbound',
                                'amount': rec.amount_total,
                                'currency_id': 1,
                                'partner_id': rec.partner_id.id,
                                'partner_type': 'customer',
                            }
                            payment = payment_model.create(post_fixed)
                            payment.post()
                    else:
                        ex_ai.append(code_transfer)
                    name_so.write({'x_status_invoice': "Doanh thu đã chuyển về tài khoản"})
                else :
                    excep_so.append(code_transfer)
                index = index + 1
            if ex_ai:
                message = "Chưa tạo được invoice cho SO có mã vận đơn hoặc invoice chưa ở trạng thái open : " + str(",".join(ex_ai))
                raise osv.except_osv("Cảnh báo !", message)
            if excep_so:
                message = "Không tìm thấy SO hoặc số tiền không khớp : " + str(",".join(excep_so))
                raise osv.except_osv("Cảnh báo !", message)
            self.file_import = None
        except IndexError:
            raise osv.except_orm("Error", "Thiếu cột dữ liệu")

    @api.multi
    def import_shipping_fee_money(self, context=None):
        # kiểm tra file có rỗng
        if self.file_import is None:
            raise osv.except_orm('Error', 'File is not empty')
        # Kiểm tra định dạng file
        self.check_format_file_excel(self.file_import_name)
        # tiến hành đọc file
        file_import = self.file_import
        data = base64.decodestring(file_import)
        excel = xlrd.open_workbook(file_contents=data)
        sheet = excel.sheet_by_index(0)
        excep_so = []
        try:
            index = 1
            so_obj = self.env['sale.order']
            while index < sheet.nrows:
                shipping_id = sheet.cell(index, 0).value
                shipping_id_money = sheet.cell(index, 1).value
                if self.is_number(shipping_id_money) == False:
                    message = "Số tiền không thể là chữ: " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                if self.is_number(shipping_id) == True:
                    shipping_id = str(int(shipping_id))
                sale_order = so_obj.search([('shipping_id', '=', shipping_id)],limit = 1)
                if sale_order :
                    sale_order.write({'shipping_fee': shipping_id_money,'x_check_viettel':1})
                else :
                    excep_so.append(shipping_id)
                index = index + 1
            if excep_so:
                message = "Không tìm thấy mã vận đơn : " + str(",".join(excep_so))
                raise osv.except_osv("Cảnh báo !", message)
            self.file_import = None
        except IndexError:
            raise osv.except_orm("Error", "Thiếu cột dữ liệu")

    @api.multi
    def import_shipping_fee_money_return(self, context=None):
        # kiểm tra file có rỗng
        if self.file_import is None:
            raise osv.except_orm('Error', 'File is not empty')
        # Kiểm tra định dạng file
        self.check_format_file_excel(self.file_import_name)
        # tiến hành đọc file
        file_import = self.file_import
        data = base64.decodestring(file_import)
        excel = xlrd.open_workbook(file_contents=data)
        sheet = excel.sheet_by_index(0)
        excep_so = []
        try:
            index = 1
            so_obj = self.env['sale.order']
            while index < sheet.nrows:
                shipping_id = sheet.cell(index, 0).value
                shipping_id_money = sheet.cell(index, 1).value
                if self.is_number(shipping_id_money) == False:
                    message = "Số tiền không thể là chữ: " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                if self.is_number(shipping_id) == True:
                    shipping_id = str(int(shipping_id))
                sale_order = so_obj.search([('shipping_id_return', '=', shipping_id)],limit = 1)
                if sale_order :
                    sale_order.write({'shipping_fee_return': shipping_id_money,'x_check_viettel':3})
                else :
                    excep_so.append(shipping_id)
                index = index + 1
            if excep_so:
                message = "Không tìm thấy mã vận đơn hoàn: " + str(",".join(excep_so))
                raise osv.except_osv("Cảnh báo !", message)
            self.file_import = None
        except IndexError:
            raise osv.except_orm("Error", "Thiếu cột dữ liệu")

    @api.multi
    def save_file_tab_cod(self, context=None):
        # kiểm tra file có rỗng
        if self.file_import is None:
            raise osv.except_orm('Error', 'File is not empty')
        # Kiểm tra định dạng file
        self.check_format_file_excel(self.file_import_name)
        # tiến hành đọc file
        file_import = self.file_import
        data = base64.decodestring(file_import)
        excel = xlrd.open_workbook(file_contents=data)
        sheet = excel.sheet_by_index(0)
        try:
            index = 1
            so_obj = self.env['sale.order']
            do_obj = self.env['stock.picking']
            ai_obj = self.env['account.invoice']
            stock_immediate_transfer = self.env['stock.immediate.transfer']
            excep_so = []
            while index < sheet.nrows:
                code_transfer = sheet.cell(index, 0).value
                money = sheet.cell(index, 1).value or 0
                if self.is_number(code_transfer) == True:
                    code_transfer = str(int(code_transfer))
                if self.is_number(money) == False:
                    message = "Số tiền không thể là chữ: " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                name_so = so_obj.search([('shipping_id', '=', code_transfer)],limit = 1)
                if name_so :
                    excep_money = []
                    stock_picking_ids = do_obj.search([('group_id.name','=',name_so.name)])
                    for sp in stock_picking_ids :
                        if sp.amount_total == money:
                            if sp.name.find('PICK') != -1 and sp.state and sp.state == "waiting":
                                sp.force_assign()
                            if sp.picking_type_id.id == self.env.ref(
                                    'stock.picking_type_out').id and sp.state and sp.state == "waiting":
                                sp.force_assign()
                            if sp.name.find('PICK') != -1 and sp.state and sp.state == "assigned":
                                sp.button_validate()
                                sits = stock_immediate_transfer.search([])
                                for sit in sits:
                                    sit[0].process()
                            if sp.picking_type_id.id == self.env.ref(
                                    'stock.picking_type_out').id and sp.state and sp.state == "assigned":
                                sp.button_validate()
                                # sit = stock_immediate_transfer.search([('pick_ids', '=', sp.id)])
                                # sit[-1].process()
                                sits = stock_immediate_transfer.search([])
                                for sit in sits:
                                    sit[0].process()
                                so = self.env['sale.order'].browse(
                                    sp.group_id.sale_id.id)
                                if so:
                                    so.write({'x_status_do': 3})
                        else :
                            excep_money.append(code_transfer)
                            break
                    if excep_money :
                        message = "Tiền của mã vận đơn không khớp: " + str(",".join(excep_money))
                        raise osv.except_osv("Cảnh báo !", message)
                    account_invoice = ai_obj.search([('origin', '=', name_so.name), ('state', '=', 'draft')])
                    if account_invoice:
                        for rec in account_invoice:
                            rec.write({'date_invoice': self.invoice_date})
                            rec.action_invoice_open()
                    else:
                        message = "Chưa tạo được invoice cho SO có mã vận đơn ở dòng : " + str(
                            index + 1)
                        raise osv.except_osv("Cảnh báo !", message)
                else :
                    excep_so.append(code_transfer)
                index = index + 1
            if excep_so:
                message = "Không tìm thấy SO : " + str(",".join(excep_so))
                raise osv.except_osv("Cảnh báo !", message)
            self.file_import = None
        except IndexError:
            raise osv.except_orm("Error", "Thiếu cột dữ liệu")

    @api.multi
    def import_shipping_fee(self, context=None):
        # kiểm tra file có rỗng
        if self.file_import is None:
            raise osv.except_orm('Error', 'File is not empty')
        # Kiểm tra định dạng file
        self.check_format_file_excel(self.file_import_name)
        # tiến hành đọc file
        file_import = self.file_import
        data = base64.decodestring(file_import)
        excel = xlrd.open_workbook(file_contents=data)
        sheet = excel.sheet_by_index(0)
        excep_so = []
        dublicate_ship = []
        try:
            index = 1
            so_obj = self.env['sale.order']
            index2 = 1
            while index2 < sheet.nrows:
                shipping_id2 = sheet.cell(index2, 1).value
                if self.is_number(shipping_id2) == True:
                    shipping_id2 = str(int(shipping_id2))
                sale_order = so_obj.search([('shipping_id', '=', shipping_id2)], limit=1)
                if sale_order:
                    dublicate_ship.append(shipping_id2)
                index2 = index2 +1
            if dublicate_ship:
                message = "Mã Vận Đơn Đã Tồn Tại : " + str(",".join(dublicate_ship))
                raise osv.except_osv("Cảnh báo !", message)
            while index < sheet.nrows:
                name = sheet.cell(index, 0).value
                shipping_id = sheet.cell(index, 1).value
                carrier = sheet.cell(index, 2).value
                if self.is_number(shipping_id) == True:
                    shipping_id = str(int(shipping_id))
                if self.is_number(name) == True:
                    message = "Tên SO không thể là số: " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                carrier_obj = self.env['delivery.carrier'].search([('name','=',carrier)],limit = 1)
                if carrier_obj:
                    carrier_id = carrier_obj[0].id
                else :
                    message = "Không tìm thấy phương án giao hàng : " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                sale_order = so_obj.search([('name', '=', name)],limit = 1)
                if sale_order :
                    sale_order.write({'shipping_id': shipping_id,'carrier_id':carrier_id})
                else :
                    excep_so.append(name)
                index = index + 1
            if excep_so:
                message = "Không tìm thấy SO : " + str(",".join(excep_so))
                raise osv.except_osv("Cảnh báo !", message)
            self.file_import = None
        except IndexError:
            raise osv.except_orm("Error", "Thiếu cột dữ liệu")

    @api.multi
    def import_shipping_fee_return(self, context=None):
        # kiểm tra file có rỗng
        if self.file_import is None:
            raise osv.except_orm('Error', 'File is not empty')
        # Kiểm tra định dạng file
        self.check_format_file_excel(self.file_import_name)
        # tiến hành đọc file
        file_import = self.file_import
        data = base64.decodestring(file_import)
        excel = xlrd.open_workbook(file_contents=data)
        sheet = excel.sheet_by_index(0)
        try:
            index = 1
            so_obj = self.env['sale.order']
            excep_so = []
            dublicate_ship =[]
            index2 = 1
            while index2 < sheet.nrows:
                shipping_id2 = sheet.cell(index2, 1).value
                if self.is_number(shipping_id2) == True:
                    shipping_id2 = str(int(shipping_id2))
                sale_order = so_obj.search([('shipping_id_return', '=', shipping_id2)], limit=1)
                if sale_order:
                    dublicate_ship.append(shipping_id2)
                index2 = index2 +1
            if dublicate_ship:
                message = "Mã Vận Đơn Hoàn Đã Tồn Tại : " + str(",".join(dublicate_ship))
                raise osv.except_osv("Cảnh báo !", message)
            while index < sheet.nrows:
                name = sheet.cell(index, 0).value
                shipping_id = sheet.cell(index, 1).value
                if self.is_number(shipping_id) == True:
                    value_shipping = str(int(shipping_id))
                else:
                    value_shipping = shipping_id
                if self.is_number(name) == True:
                    message = "Tên SO không thể là số: " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)

                sale_order = so_obj.search([('name', '=', name)],limit = 1)
                if sale_order:
                    sale_order.write({'shipping_id_return': value_shipping})
                else :
                    excep_so.append(name)
                index = index + 1
            if excep_so:
                message = "Không tìm thấy SO : " + str(",".join(excep_so))
                raise osv.except_osv("Cảnh báo !", message)
            self.file_import = None
        except IndexError:
            raise osv.except_orm("Error", "Thiếu cột dữ liệu")
    @api.multi
    def import_update_do(self, context=None):
        # kiểm tra file có rỗng
        if self.file_import is None:
            raise osv.except_orm('Error', 'File is not empty')
        # Kiểm tra định dạng file
        self.check_format_file_excel(self.file_import_name)
        # tiến hành đọc file
        file_import = self.file_import
        data = base64.decodestring(file_import)
        excel = xlrd.open_workbook(file_contents=data)
        sheet = excel.sheet_by_index(0)
        excep_so = []
        try:
            index = 1
            so_obj = self.env['sale.order']
            do_obj = self.env['stock.picking']
            stock_immediate_transfer = self.env['stock.immediate.transfer']
            StockReturnPicking = self.env['stock.return.picking']

            # print stock_immediate_transfer
            # print StockReturnPicking
            while index < sheet.nrows:
                shipping_id = sheet.cell(index, 0).value
                x_status_do = sheet.cell(index, 1).value

                if self.is_number(x_status_do) == False:
                    message = "Trạng thái vận chuyển phải  bằng số: " + str(index + 1)
                    raise osv.except_osv("Cảnh báo !", message)
                if self.is_number(shipping_id) == True:
                    shipping_id = str(int(shipping_id))
                name_so = so_obj.search(['|',('shipping_id', '=', shipping_id),('shipping_id_return','=',shipping_id)], limit=1)

                if name_so:
                    stock_picking_ids = do_obj.search([('group_id.name','=', name_so.name)])
                    if stock_picking_ids:
                        for sp in stock_picking_ids:
                            #Đơn Đang Đi Đường
                            if int(x_status_do) == 2:
                                # print("sp_nam_pick", sp.name.find('PICK'))
                                # print("sp state \n", sp.state)
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "waiting":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "confirmed":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "assigned":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.button_validate()
                                if sp.picking_type_id.id and sp.state and sp.state == "waiting":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                name_so.write({'x_status_do': 2})
                            # Đơn thành Công
                            if int(x_status_do) == 3:
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "confirmed":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "waiting":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                # print(sp.picking_type_id.id, "===" ,self.env.ref('stock.picking_type_out').id)
                                if sp.picking_type_id.id and sp.state and sp.state == "confirmed":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                if sp.picking_type_id.id and sp.state and sp.state == "waiting":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                if sp.name.find('PICK') != -1 and sp.state and  sp.state == "assigned":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.button_validate()
                                if sp.picking_type_id.id and sp.state and sp.state == "assigned":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.button_validate()
                                if name_so :
                                    sp.partner_id.level = 6
                                    name_so.write({'x_status_do': 3})
                            # Đơn hoàn
                            if int(x_status_do) == 4 and name_so.x_status_do != 7:
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "waiting":
                                    sp.force_assign()
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "confirmed":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                if sp.name.find('PICK') != -1 and sp.state and  sp.state == "assigned":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.button_validate()
                                    # sits = stock_immediate_transfer.search([])
                                    # for sit in sits:
                                    #     sit[0].process()
                                if sp.name.find('PICK') != -1 and sp.state and  sp.state == "done":
                                    flag = True
                                    for r in stock_picking_ids:
                                        if r.name.find('RETURN') != -1:
                                            flag = False
                                    if flag:

                                        default_data = StockReturnPicking.with_context(active_id=sp.id).default_get(
                                            ['move_dest_exists', 'original_location_id', 'product_return_moves',
                                             'parent_location_id', 'location_id'])
                                        return_wiz = StockReturnPicking.with_context(active_id=sp.id).create(default_data)

                                        # for it in sp.pack_operation_product_ids:
                                        #     for item in return_wiz.product_return_moves:
                                        #         if item.product_id == it.product_id:
                                        #             item.quantity = it.product_qty
                                        return_wiz.create_returns()
                                if sp.picking_type_id.id and sp.state and sp.state != "done" :
                                    sp.action_cancel()
                                if name_so:
                                    name_so.write({'x_status_do': 4})

                            #Đơn đã nhập kho hoàn
                            if int(x_status_do) == 7:
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "waiting":
                                    sp.force_assign()
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "confirmed":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.force_assign()
                                if sp.name.find('PICK') != -1 and sp.state and sp.state == "assigned":
                                    for move_line in sp.move_lines:
                                        move_line.quantity_done = move_line.product_uom_qty
                                    sp.button_validate()
                                if sp.name.find('PICK') != -1 and sp.state and  sp.state == "done":
                                    flag = True
                                    for r in stock_picking_ids:
                                        if r.name.find('RETURN') != -1:
                                            flag = False
                                    if flag:
                                        default_data = StockReturnPicking.with_context(active_id=sp.id).default_get(
                                            ['move_dest_exists', 'original_location_id', 'product_return_moves',
                                             'parent_location_id', 'location_id'])

                                        return_wiz = StockReturnPicking.with_context(active_id=sp.id).create(default_data)
                                        return_wiz.create_returns()
                                    stock_picking_ids_new = do_obj.search([('group_id.name', '=', name_so.name)])
                                    for sp_new in stock_picking_ids_new:
                                        if sp_new.name.find('RETURN') != -1 and sp_new.state and sp_new.state == "assigned":
                                            # sits = stock_immediate_transfer.search([])
                                            # for sit in sits:
                                            #     sit[0].process()
                                            sp_new.button_validate()
                                if sp.picking_type_id.id and sp.state and sp.state != "done":
                                    sp.action_cancel()
                                if sp.name.find('RETURN') != -1 and sp.state and sp.state == "assigned":
                                    # sits = stock_immediate_transfer.search([])
                                    # for sit in sits:
                                    #     sit[0].process()
                                    sp.button_validate()
                                if name_so:
                                    name_so.write({'x_status_do': 7})
                    else:
                        message = "Không tìm thấy DO : " + str(index + 1)
                        raise osv.except_osv("Cảnh báo !", message)
                else :
                    excep_so.append(shipping_id)
                index = index + 1
            if excep_so:
                message = "Không tìm thấy SO có mã vận đơn : " + str(",".join(excep_so))
                raise osv.except_osv("Cảnh báo !", message)
            self.file_import = None
        except IndexError:
            raise osv.except_orm("Error", "Thiếu cột dữ liệu")
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def check_format_file_excel(self, file_name):
        if file_name == False:
            raise osv.except_osv("Warning!", ("File name not found"))
        if file_name.endswith('.xls') == False and file_name.endswith('.xlsx') == False:
            self.file_import = None
            self.file_import_name = None
            raise osv.except_osv("Error!", ("Change the file type as .xlsx or .xls"))