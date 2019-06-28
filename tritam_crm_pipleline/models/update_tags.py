# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError


class ChangeActiveCustomer(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def update_force_assign(self):
        # list_id = ['SO1391', 'SO1484', 'SO1622', 'SO1623', 'SO1624', 'SO1625', 'SO1626', 'SO1627', 'SO1628', 'SO1630',
        #            'SO1631', 'SO1632', 'SO1633', 'SO1634', 'SO1635', 'SO1636', 'SO1638', 'SO1639', 'SO1640', 'SO1642',
        #            'SO1643', 'SO1644', 'SO1645', 'SO1646', 'SO1647', 'SO1649', 'SO1650', 'SO1651', 'SO1652', 'SO1653',
        #            'SO1654', 'SO1655', 'SO1656', 'SO1657', 'SO1658', 'SO1659', 'SO1660', 'SO1661', 'SO1662', 'SO1663',
        #            'SO1664', 'SO1665',
        #            ]
        # if list_id:
        #     sp = self.env['sale.order'].search([('name', '=', list_id)])
        #     for s in sp:
        #         s.shipping_id = False
        #
        # list_hoanthanh = ['SO1391', 'SO1484', 'SO1622', 'SO1623', 'SO1624', 'SO1625', 'SO1626', 'SO1627', 'SO1628',
        #                   'SO1631', 'SO1632', 'SO1635', 'SO1636', 'SO1639', 'SO1640', 'SO1642', 'SO1644', 'SO1645',
        #                   'SO1646', 'SO1647', 'SO1649', 'SO1651', 'SO1653', 'SO1654', 'SO1655', 'SO1657', 'SO1658',
        #                   'SO1659', 'SO1660', 'SO1661', 'SO1662', 'SO1663', 'SO1664', 'SO1665', ]
        # if list_hoanthanh:
        #     so_ht = self.env['sale.order'].search([('name', '=', list_hoanthanh)])
        #
        #     for s_h in so_ht:
        #         s_h.x_status_do = 3

        # list_hoan = ['SO50435','SO50441', 'SO50445']
        # list_vd = ['10733414465', '10733414512', '10733414668']
        # if list_hoan:
        #     so_h = self.env['sale.order'].search([('name', '=', list_hoan)])
        #     for so in so_h:
        #         for i in list_vd:
        #             so.shipping_id = i

        return True
