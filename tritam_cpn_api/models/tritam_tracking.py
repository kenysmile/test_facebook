# -*- coding: utf-8 -*-

from odoo import models, fields ,exceptions, api,_
from . import tritam_api_constant

import requests
import json
from datetime import datetime
from suds.client import Client
import logging
_logger = logging.getLogger(__name__)

Constant = tritam_api_constant.Constant
class tritam_tracking(models.Model):
    _name = "tritam.tracking"

    tracking_code = fields.Char(string=_(u"Mã bưu gửi"))
    order_number = fields.Char(string=_(u"Số Hóa đơn"))

    @api.model
    def login_vtp(self):
        url = 'http://api.vtp.vn/api/seller/public/api/v1/auth/login'
        data = {'email': '{}'.format(Constant.VtPost.EMAIL), 'password': '{}'.format(Constant.VtPost.PASSWD)}
        header = {'content-type': 'application/json'}
        re = requests.post(url, params=data, headers=header)
        result = json.loads(re.content)
        if re.status_code == 200:
            token_ = json.loads(re.content)['data']['token']['key']
            return {'success': True, 'token_key': token_, 'message': result['message']}
        else:
            return {'success': False, 'message': result['message']}

    # @api.model
    # def register_vtp(self, reg_email, reg_passwd, reg_name, reg_phone, reg_addr, reg_gender, reg_city_id,
    #                  reg_district_id, reg_ward_id):
    #     url = 'http://api.vtp.vn/api/seller/public/api/v1/auth/register'
    #     data = {
    #         u"email": reg_email,
    #         u"password": reg_passwd,
    #         u"fullname": reg_name,
    #         u"phone": reg_phone,
    #         u"address": reg_addr,
    #         u"identifier": reg_gender,
    #         u"location": {
    #             u"city_id": reg_city_id,
    #             u"district_id": reg_district_id,
    #             u"ward_id": reg_ward_id,
    #             u"": u""
    #         }
    #     }
    #     headers = {'content-type': 'application/json'}
    #     data = json.dumps(data)
    #     res = requests.post(url, data=data, headers=headers)
    #     if res.status_code != 200:
    #         raise ValueError(u'Kiểm tra lại kết nối')
    #     res = json.loads(res.content)
    #     if res['error'] is True:
    #         raise ValueError(res['error_message'])
    #     mess = res['message']
    #     return mess

    @api.model
    def create_order_vtp(self, pick_city_id, pick_district_id, pick_inventory_number, pick_ward_id, pick_address,
                         pick_phone, pick_fullname, cf_service_code, cf_weight, cf_amount, cf_quantity, cf_collection,
                         cf_vas, cf_censorship, cf_payment, cf_type, de_city_id, de_district_id, de_ward_id, de_address,
                         de_phone, de_fullname, parcel_items_weight, parcel_items_amount, parcel_items_quanlity,
                         parcel_items_description, parcel_items_product_name, parcel_total_amount, parcel_total_weight,sale_order_number):
        login_info = self.login_vtp()
        if login_info['success'] is False:
            raise ValueError("Login to Viettel Post Fasle")
        token = login_info['token_key']
        url = 'http://api.vtp.vn/api/v2/create_order?access_token={}'.format(token)
        data = {
            u"Domain": u"Tri Tâm",
            u"Pickup": {
                u"CityId": pick_city_id,
                u"DistrictId": pick_district_id,
                u"InventoryNumber": pick_inventory_number,
                u"WardId": pick_ward_id,
                u"Address": pick_address,
                u"Phone": pick_phone,
                u"FullName": pick_fullname,
            },
            u"Config": {
                u"Service": cf_service_code,
                u"Type": cf_type,
                u"Weight": cf_weight,
                u"Amount": cf_amount,
                u"Quantity": cf_quantity,
                u"Payment": cf_payment,
                u"Collection": cf_collection,
                u"Vas": [
                  # cf_vas
                ],
                u"Censorship": cf_censorship,
            },
            u"Delivery": {
                u"CityId": de_city_id,
                u"DistrictId": de_district_id,
                u"Address": de_address,
                u"WardId": de_ward_id,
                u"Phone": de_phone,
                u"FullName": de_fullname,
            },
            # u"ParcelItems": [
            #     {
            #       u"Items": [
            #         {
            #           u"Weight": parcel_items_weight,
            #           u"Amount": parcel_items_amount,
            #           u"Quanlity": parcel_items_quanlity,
            #           u"Description": parcel_items_description,
            #           u"ProductName": parcel_items_product_name,
            #         }
            #       ],
            #       u"TotalAmount": parcel_total_amount,
            #       u"TotalWeight": parcel_total_weight,
            #     }
            # ]
        }
        headers = {'content-type': 'application/json'}
        data = json.dumps(data)
        res = requests.post(url, data=data, headers=headers)
        if res.status_code != 200:
            _logger.info(u'Chưa Loggin được')
            raise Warning("Kiểm tra lại kết nối/dữ liệu")
        res_data = json.loads(res.content)
        if res_data['Success'] is False:
            _logger.info("Sai Dữ Liệu Đầu Vào")
            raise Warning(u'Create Order False, plz try again!')
        if res_data['Success'] is True:
            self.create({
                'tracking_code': res_data['Data']['OrderNumber'],
                'order_number': sale_order_number,
            })
            _logger.info({'tracking_code':res_data['Data']['OrderNumber']})
        return res_data
    
    @api.model
    def cancel_order_vtp(self, ordernumber):
        login_info = self.login_vtp()
        if login_info['success'] is False:
            raise ValueError("Login to Viettel Post Fasle")
        token = login_info['token_key']
        url = 'http://api.vtp.vn/api/v1/cancel_order?access_token={}'.format(token)
        data = {
            "OrderNumber": ordernumber,
        }
        headers = {'content-type': 'application/json'}
        data = json.dumps(data)
        res = requests.post(url, data=data, headers=headers)
        if res.status_code != 200:
            raise ValueError(u"Mã đơn không tồn tại. Vui lòng kiểm tra lại!")
        res_data = json.loads(res.content)
        return res_data['Messages']


tritam_tracking()


class tritam_tracking_journey(models.Model):
    _name = "tritam.tracking.journey"

    tracking_code = fields.Char(string=_(u"Mã bưu gửi"))
    status_name = fields.Char(string=_(u"Trạng thái vận thư"))
    location = fields.Char(string=_(u"Địa điểm"))
    note = fields.Char(string=_(u"Ghi chú"))
    time_create = fields.Datetime(string=_(u"Thời gian"))

    @api.model
    def create_tracking_journey(self, json_data=None):

        try:
            data = json.loads(json_data)
            tracking_code = data.get('tracking_code', False)
            if tracking_code is False:
                return {'success': False, 'error_id': Constant.TritamPost.ERROR_JOURNEY.ERROR_REQUIRED,
                        'message': 'The tracking code cannot be found.'}

            status_name = data.get('status_name', False)
            if status_name is False:
                return {'success': False, 'error_id': Constant.TritamPost.ERROR_JOURNEY.ERROR_REQUIRED,
                        'message': 'The status name cannot be found.'}

            location = data.get('location', False)
            if location is False:
                return {'success': False, 'error_id': Constant.TritamPost.ERROR_JOURNEY.ERROR_REQUIRED,
                        'message': 'The location cannot be found.'}

            note = data.get('note', '')

            time_create = data.get('time_create', False)
            if time_create is False:
                return {'success': False, 'error_id': Constant.TritamPost.ERROR_JOURNEY.ERROR_REQUIRED,
                        'message': 'The time_create cannot be found.'}
            try:
                time_create = datetime.datetime.strptime(time_create, '%d-%m-%Y %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S').decode('unicode-escape')
            except:
                return {'success': False, 'error_id': Constant.TritamPost.ERROR_JOURNEY.ERROR_INPUT,
                            'message': 'The time create must be format "%d-%m-%Y %H:%M:%S".'}

            # self.create({'tracking_code': tracking_code, 'status_name': status_name, 'location': location, 'note': note,'time_create': time_create})
            return {'success': True, 'error_id': Constant.TritamPost.ERROR_JOURNEY.SUCESS, 'message': 'Done'}
        except:
            return {'success': False, 'error_id': Constant.TritamPost.ERROR_JOURNEY.ERROR_INPUT, 'message': 'The tracking journey cannot be created. Maybe has been an error processing json format'}

tritam_tracking_journey()