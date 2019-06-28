# -*- coding: utf-8 -*-
from odoo import models, fields ,exceptions, api,_

import requests
import json
from datetime import datetime
from suds.client import Client


class tritam_res_partner(models.Model):
    _inherit = 'res.partner'

    def import_location(self):
        url = 'http://api.vtp.vn/api/province'

        payload = "{}"
        header = {'content-type': 'application/json'}
        re = requests.get(url, params=payload,headers=header)
        result = json.loads(re.content)
        for i in range(0, len(result['_embedded']['province'])):
            name = result['_embedded']['province'][i]['Name']
            code = result['_embedded']['province'][i]['ProvinceId']
            self.env['res.country'].create({
                'name': name,
                'code': code,
                })
            url2 = 'http://api.vtp.vn/api/district?province={code}'.format(code=code)
            re_dic = requests.get(url2, params=payload,headers=header)
            result_dic = json.loads(re_dic.content)
            for x in range(0, len(result_dic['_embedded']['district'])):
                name_dic = result_dic['_embedded']['district'][x]['Name']
                code_dic = result_dic['_embedded']['district'][x]['DistrictId']
                self.env['res.country.state'].create({
                    'name': name_dic,
                    'code': code_dic,
                    'code_provine': code,
                })

                url3 = 'http://api.vtp.vn/api/ward?district={code}'.format(code=code_dic)
                re_ward = requests.get(url3, params=payload, headers=header)
                result_ward = json.loads(re_ward.content)
                for z in range(0, len(result_ward['_embedded']['ward'])):
                    name_ward = result_ward['_embedded']['ward'][z]['Name']
                    code_ward = result_ward['_embedded']['ward'][z]['WardId']
                    self.env['tritam.tracking.location.ward'].create({
                        'name': name_ward,
                        'code_District': code_dic,
                        'code_ward': code_ward,
                    })





