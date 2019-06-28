# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Caidatphanbo(models.Model):
    _name = 'res.automatic.share.settings'
    _inherit = 'res.config.settings'
    _order = 'id desc'

    conf_support_recall_to_new = fields.Integer()
    conf_resign_recall_to_new = fields.Integer()
    conf_resign_sp_to_new = fields.Integer()

    conf_new_contact = fields.Integer()
    conf_re_use = fields.Integer()
    conf_re_sign = fields.Integer()
    conf_new_cts_knm = fields.Integer()
    # team_mkt = fields.Many2one('hr.department', string='Team MKT')
    # team_mkt = fields.Selection([(27, 'MKT Khánh'),
    #                              (5, 'MKT Văn'),
    #                              (4, 'MKT Tuấn'),
    #                              (31, 'MKT Bảo'),
    #                              (32, 'MKT Thủy Tuấn'),
    #                              (26, 'MKT Hiếu'),
    #                              (16, 'MKT Trường'),
    #                              (17, 'MKT Zalo'),
    #                              (11, 'MKT OS Tú'),
    #                              (35, 'MKT OS Trường')], default=27)
    # # level = fields.Integer()
    # num_cts = fields.Integer()

    @api.model
    def get_conf_new_contact(self, fields):
        conf_new_contact = self.env['ir.values'].get_defaults_dict('res.automatic.share.settings').get('number_use')
        conf_re_use = self.env['ir.values'].get_defaults_dict('res.automatic.share.settings').get('conf_re_use')
        conf_re_sign = self.env['ir.values'].get_defaults_dict('res.automatic.share.settings').get('conf_re_sign')
        conf_new_cts_knm = self.env['ir.values'].get_defaults_dict('res.automatic.share.settings').get('conf_new_cts_knm')

        # team_mkt = self.env['ir.values'].get_defaults_dict('res.automatic.share.settings').get('team_mkt')
        # # level = self.env['ir.values'].get_defaults_dict(
        # #     'res.automatic.share.settings').get('level')
        # num_cts = self.env['ir.values'].get_defaults_dict(
        #     'res.automatic.share.settings').get('num_cts')
        return {
            'conf_new_contact': conf_new_contact,
            'conf_re_use': conf_re_use,
            'conf_re_sign': conf_re_sign,
            'conf_new_cts_knm': conf_new_cts_knm,
            # 'team_mkt': team_mkt,
            # # 'level': level,
            # 'num_cts': num_cts
            }

    @api.model
    def set_conf_new_contact(self):
        set_conf_new_contact = self.env['ir.values'].sudo().set_default(
            'res.automatic.share.settings', 'conf_new_contact', self.conf_new_contact)
        set_conf_re_use = self.env['ir.values'].sudo().set_default(
            'res.automatic.share.settings', 'conf_re_use', self.conf_re_use)
        set_conf_re_sign = self.env['ir.values'].sudo().set_default(
            'res.automatic.share.settings', 'conf_re_sign', self.conf_re_sign)
        set_conf_new_cts_knm = self.env['ir.values'].sudo().set_default(
            'res.automatic.share.settings', 'conf_new_cts_knm', self.conf_new_cts_knm)
        # set_team_mkt = self.env['ir.values'].sudo().set_default(
        #     'res.automatic.share.settings', 'team_mkt', self.team_mkt)
        # set_num_cts = self.env['ir.values'].sudo().set_default(
        #     'res.automatic.share.settings', 'num_cts', self.num_cts)

        return set_conf_new_contact, set_conf_re_use, set_conf_re_sign, set_conf_new_cts_knm

    # Set/Get New care -> Care today
    @api.model
    def get_conf_support_recall_to_new(self):
        conf_support_recall_to_new = self.env['ir.values'].get_defaults_dict(
            'res.automatic.share.settings').get('conf_support_recall_to_new')
        return {'conf_support_recall_to_new' : conf_support_recall_to_new}

    @api.model
    def set_conf_support_recall_to_new(self):
        set_conf_support_recall_to_new = self.env[
            'ir.values'].sudo().set_default(
            'res.automatic.share.settings', 'conf_support_recall_to_new',
            self.conf_support_recall_to_new)
        return set_conf_support_recall_to_new

    # Set/Get Care today -> New resign
    @api.model
    def get_conf_resign_recall_to_new(self):
        conf_resign_recall_to_new = self.env['ir.values'].get_defaults_dict(
            'res.automatic.share.settings').get('conf_resign_recall_to_new')
        return {'conf_resign_recall_to_new': conf_resign_recall_to_new}

    @api.model
    def set_conf_resign_recall_to_new(self):
        set_conf_resign_recall_to_new = self.env[
            'ir.values'].sudo().set_default(
            'res.automatic.share.settings', 'conf_resign_recall_to_new',
            self.conf_resign_recall_to_new)
        return set_conf_resign_recall_to_new

    # Set/Get Resign Success -> New Resign
    @api.model
    def get_conf_resign_sp_to_new(self):
        conf_resign_sp_to_new = self.env['ir.values'].get_defaults_dict(
            'res.automatic.share.settings').get('conf_resign_sp_to_new')
        return {'conf_resign_sp_to_new': conf_resign_sp_to_new}

    @api.model
    def set_conf_resign_sp_to_new(self):
        set_conf_resign_sp_to_new = self.env[
            'ir.values'].sudo().set_default(
            'res.automatic.share.settings', 'conf_resign_sp_to_new',
            self.conf_resign_sp_to_new)
        return set_conf_resign_sp_to_new
