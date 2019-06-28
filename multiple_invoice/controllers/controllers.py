# -*- coding: utf-8 -*-
from odoo import http

# class SaleProductCustom(http.Controller):
#     @http.route('/sale_product_custom/sale_product_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_product_custom/sale_product_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_product_custom.listing', {
#             'root': '/sale_product_custom/sale_product_custom',
#             'objects': http.request.env['sale_product_custom.sale_product_custom'].search([]),
#         })

#     @http.route('/sale_product_custom/sale_product_custom/objects/<model("sale_product_custom.sale_product_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_product_custom.object', {
#             'object': obj
#         })