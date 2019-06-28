# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError
import calendar
from datetime import datetime, timedelta, date

class AccountPaymentInherit(models.TransientModel):
    _inherit = 'account.register.payments'

    amount_shipp = fields.Monetary(string='Phí ship', required=True)
    total_money = fields.Monetary(string='Tổng tiền thu được', required=True)

    @api.multi
    def create_payment(self):
        res = super(AccountPaymentInherit, self).create_payment()
        # product = self.env['product.product'].search([('can_be_expensed','=',True)],limit = 1)
        # employ = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # bank_journal_id = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        # if product and employ and bank_journal_id:
        #     create = self.env['hr.expense'].sudo().create({
        #                     'name': product.name,
        #                     'product_id':product.id,
        #                     'unit_amount': self.amount_shipp,
        #                     'employee_id':employ.id,
        #                     'payment_mode':"company_account"
        #                 })
        #     create_sheet = self.env['hr.expense.sheet'].sudo().create({
        #                     'name': create.name,
        #                     'employee_id':create.employee_id.id,
        #                     'bank_journal_id': bank_journal_id.id,
        #                     'expense_line_ids':[(4, create.id, 0)]
        #                 })
        #     create_sheet.approve_expense_sheets()
        #     create_sheet.action_sheet_move_create()
        for rec in self.invoice_ids:
            obj_so = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1)
            if obj_so :
                obj_so.write({'x_status_invoice': "Doanh thu đã chuyển về tài khoản"})
        # else:
        #     raise UserError(_("Không có sản phẩm phí ship hoặc user này không phải là employee hoặc không có Bank journal có type là Bank "))
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        # Empty self can happen if the user tries to reconcile entries which are already reconciled.
        # The calling method might have filtered out reconciled lines.
        if not self:
            return True

        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        partners = set()
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.account_id.internal_type in ('receivable', 'payable')):
                partners.add(line.partner_id.id)
            if line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries!'))
        if len(set(all_accounts)) > 1:
            raise UserError(_('Entries are not of the same account!'))
        if not all_accounts[0].reconcile:
            raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (all_accounts[0].name, all_accounts[0].code))
        # if len(partners) > 1:
        #     raise UserError(_('The partner has to be the same on all lines for receivable and payable accounts!'))

        #reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        #if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
            #add writeoff line to reconcile algo and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
            return writeoff_to_reconcile
        return True
