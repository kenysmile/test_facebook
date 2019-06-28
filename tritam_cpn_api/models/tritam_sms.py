# -*- coding: utf-8 -*-
from odoo import models, fields ,exceptions, api,_
#from tritam_api_constant import Constant
import logging
import requests
import json
from datetime import datetime
from suds.client import Client
_logger = logging.getLogger(__name__)


class tritam_tracking(models.Model):
    _name = "tritam.sms"

    @api.model
    def send_sms_api(self,phone,content):
        # url_base = "http://rest.esms.vn/MainService.svc/json/SendMultipleMessage_V4_get?Phone={Phone}&Content={Content}&ApiKey={ApiKey}&SecretKey={SecretKey}&IsUnicode={IsUnicode}&Brandname={Brandname}&SmsType={SmsType}"
        # url = url_base.format(Phone=str(phone),Content=str(content),ApiKey=Constant.Tritamsms.APIKEY,SecretKey=Constant.Tritamsms.SECRECTKEY,IsUnicode='0',Brandname='TriTam',SmsType='2')
        # header = {'content-type': 'application/json'}
        # re = requests.get(url, headers=header)
        # result = json.loads(re.text)
        # _logger.info('---------------------Da Sent SMS-----------------------------')
        # if result['CodeResult'] == 100:
        #     _logger.info('---------------------Da Sent SMS code 100 -----------------------------')
        #     return {'success': True}
        # else:
        #     return {'success': False}
        return 1

    @api.model
    def send_sms_api_delay(self,phone,content,SendDate):
        # url_base = "http://rest.esms.vn/MainService.svc/json/SendMultipleSMSBrandname?Phone={Phone}&Content={Content}&BrandnameCode={BrandnameCode}&ApiKey={ApiKey}&SecretKey={SecretKey}&SmsType={SmsType}&SendDate={SendDate}"
        # url = url_base.format(Phone=str(phone),Content=str(content),ApiKey=Constant.Tritamsms.APIKEY,SecretKey=Constant.Tritamsms.SECRECTKEY,BrandnameCode='TriTam',SmsType='2',SendDate=SendDate)
        # header = {'content-type': 'application/json'}
        # re = requests.get(url, headers=header)
        # result = json.loads(re.text)
        # _logger.info('---------------------Da Sent SMS Delay-----------------------------')
        # if result['CodeResult'] == '100':
        #     _logger.info('---------------------Da Sent SMS  delay code 100,SMSID: '+result['SMSID'] +' -----------------------------')
        #     return {'success': True}
        # else:
        #     return {'success': False}
        return 1
