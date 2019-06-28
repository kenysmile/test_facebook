# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}


class account_register_payments(models.TransientModel):
    _name = "account.register.payments"
    _inherit = 'account.abstract.payment'
    _description = "Register payments on multiple invoices"

    invoice_ids = fields.Many2many('account.invoice', 'account_invoice_register_payments', string='List of account invoice associated to this register payments')
    amount_refund = fields.Monetary(string='Payment Amount refund')

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type:
            return {'domain': {'payment_method_id': [('payment_type', '=', self.payment_type)]}}

    def _get_invoices(self):
        return self.env['account.invoice'].browse(self._context.get('active_ids'))

    @api.model
    def default_get(self, fields):
        rec = super(account_register_payments, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'account.invoice':
            raise UserError(_("Programmation error: the expected model for this action is 'account.invoice'. The provided one is '%d'.") % active_model)

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        #if any(inv.commercial_partner_id != invoices[0].commercial_partner_id for inv in invoices):
            #raise UserError(_("In order to pay multiple invoices at once, they must belong to the same commercial partner."))
        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] for inv in invoices):
            raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

        total_amount = sum(inv.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
        total_amount_shipp = sum(inv.ai_shipping_fee for inv in invoices)
        total_money = total_amount - total_amount_shipp
        communication = ' '.join([ref for ref in invoices.mapped('number') if ref])
        amount_refund_ca = 0
        for inv_ca in invoices:
            if inv_ca.type == 'out_refund':
                amount_refund_ca = amount_refund_ca + inv_ca.residual

        rec.update({
            'amount': abs(total_amount),
            'amount_shipp': abs(total_amount_shipp),
            'total_money': abs(total_money),
            'amount_refund': amount_refund_ca,
            'invoice_ids': invoices.ids,
            'currency_id': invoices[0].currency_id.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'communication': communication,
        })
        return rec

    def get_payment_vals(self):
        """ Hook for extension """
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices()],
            'payment_type': self.payment_type,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
        }

    @api.multi
    @api.model
    def create_payment(self):
        invs_load = self._get_invoices()
        total_am = self.amount_refund + self.amount
        payment_type_fixed = self.payment_type
        journal_id_fixed = self.journal_id.id
        payment_method_id_fixed = self.payment_method_id.id
        payment_date_fixed = self.payment_date
        currency_id_fixed = self.currency_id.id
        communication_fixed = self.communication
        for inv_ in invs_load:
            amount_by_in = inv_.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv_.type]
            if payment_type_fixed == 'outbound':
                if total_am > 0:
                    amount_by_in = abs(amount_by_in)
                    total_am = total_am - amount_by_in
                    post_fixed = {
                        'journal_id': journal_id_fixed,
                        'payment_method_id': payment_method_id_fixed,
                        'payment_date': payment_date_fixed,
                        'communication': communication_fixed,
                        'invoice_ids': [(4, inv_.id, None)],
                        'payment_type': payment_type_fixed,
                        'amount': amount_by_in,
                        'currency_id': currency_id_fixed,
                        'partner_id': inv_.commercial_partner_id.id,
                        'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[inv_.type],
                    }
                    payment = self.env['account.payment'].create(post_fixed)
                    payment.post()
            else:
                if inv_.type == 'out_invoice':
                    if total_am > 0:
                        amount_by_in = abs(amount_by_in)
                        if total_am > amount_by_in:
                            pay_amount = amount_by_in
                        else:
                            pay_amount = total_am
                        total_am = total_am - amount_by_in
                        post_fixed = {
                            'journal_id': journal_id_fixed,
                            'payment_method_id': payment_method_id_fixed,
                            'payment_date': payment_date_fixed,
                            'communication': communication_fixed,
                            'invoice_ids': [(4, inv_.id, None)],
                            'payment_type': payment_type_fixed,
                            'amount': pay_amount,
                            'currency_id': currency_id_fixed,
                            'partner_id': inv_.commercial_partner_id.id,
                            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[inv_.type],
                        }
                        payment = self.env['account.payment'].create(post_fixed)
                        payment.post()
                elif inv_.type == 'out_refund':
                    amount_by_in = abs(amount_by_in)
                    post_fixed = {
                        'journal_id': journal_id_fixed,
                        'payment_method_id': payment_method_id_fixed,
                        'payment_date': payment_date_fixed,
                        'communication': communication_fixed,
                        'invoice_ids': [(4, inv_.id, None)],
                        'payment_type': 'outbound',
                        'amount': amount_by_in,
                        'currency_id': currency_id_fixed,
                        'partner_id': inv_.commercial_partner_id.id,
                        'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[inv_.type],
                    }
                    payment = self.env['account.payment'].create(post_fixed)
                    payment.post()
        return {'type': 'ir.actions.act_window_close'}
