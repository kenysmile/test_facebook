# -*- coding: utf-8 -*-
from odoo import models, fields ,exceptions, api,_
from suds.client import Client


class TrackingDistrict(models.Model):
    _inherit = "res.country.state"

    country_id = fields.Many2one('res.country', string='Country', required=True,
                                 help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')
    code = fields.Char(string='State Code', help='The state code.', required=False)
    code_provine = fields.Char(string='District')

    @api.model
    def create(self, vals):
        if 'country_id' in vals and vals['country_id']:
            code_provine = self.env['res.country'].browse(vals['country_id']).code
            vals['code_provine'] = code_provine
        return super(TrackingDistrict, self).create(vals)

    @api.onchange('country_id')
    def _onchange_country_id(self):
        self.code_provine = self.country_id.code


class TrackingWard(models.Model):
    _name = "tritam.tracking.location.ward"

    name = fields.Char(string='Ward')
    code_District = fields.Char(string="District")
    code_ward = fields.Char(string="Ward")

    @api.model
    def name_get(self):
        res = super(TrackingWard, self).name_get()
        state_id = self._context.get('state_id')
        result =[]
        code_dis = self.env['res.country.state'].search([('id','=',state_id)], limit=1).code
        obj_ward = self.search([('code_District','=',code_dis)])
        if state_id:
             for record in obj_ward:
                 result.append((record.id, record.name))
             return result
        return res