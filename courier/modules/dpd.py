# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from couriers.models import Courier
from couriers.modules import CourierBaseModule
from datetime import datetime
import requests
import json
from django.utils.translation import ugettext_lazy as _


class CourierManager(CourierBaseModule):
    def __init__(self, package_num, courier=None):
        super(CourierManager, self).__init__(package_num, courier)

        pack_num_verification(package_num)

        url = 'https://tracking.dpd.de/cgi-bin/simpleTracking.cgi?parcelNr=%s&locale=en_EN&type=1'
        if self.courier.url:
            url = self.courier.url
        url = url % package_num

        try:
            content = requests.get(url).content
        except:
            raise IOError(_('Courier server is not available. Check the server address.'))

        if "ErrorJSON" in content:
            raise Exception(_('Shipment not found'))

        try:
            json_data = json.loads('[' + content[1:-1] + ']')
            tracking_status = json_data[0]['TrackingStatusJSON']
            self.shipment_info = tracking_status['shipmentInfo']
            self.status_infos = tracking_status['statusInfos']
        except:
            raise Exception(_('Import error'))

        self.package_title['package_num'] = package_num

    def parse_package_title(self):
        try:
            self.package_title['post_code'] = self.shipment_info['receiverPostCode']
        except:
            raise Exception(_('Import error'))
        return self.package_title

    def parse_status_history(self):
        try:
            for statusInfo in self.status_infos:
                record = {}
                date_time = statusInfo['date'].replace(' ', '') + ' ' + statusInfo['time'].replace(' ', '')
                record['date_time'] = datetime.strptime(date_time, "%d/%m/%Y %H:%M")
                status_name = statusInfo['contents'][0]['label']
                courier_status_obj = self.get_status_instance(status_name)
                record['status'] = courier_status_obj
                record['location'] = statusInfo['city']

                if record['date_time'] > self.current_datetime:
                    self.current_datetime = record['date_time']
                    self.current_status = record['status']

                self.status_history.append(record)
        except:
            raise Exception(_('Import error'))

        self.package_title['current_status'] = self.current_status
        return self.status_history