# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from couriers.models import Courier
from couriers.modules import CourierBaseModule
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from django.utils.translation import ugettext_lazy as _


class CourierManager(CourierBaseModule):
    def __init__(self, package_num, courier=None):
        super(CourierManager, self).__init__(package_num, courier)

        pack_num_verification(package_num)

        url = 'http://pewnapaczka.pl/tnt_szczegoly.php?nr=%s'
        if self.courier.url:
            url = self.courier.url
        url = url % package_num

        try:
            content = requests.get(url).content
        except:
            raise IOError(_('Courier server is not available. Check the server address.'))

        self.soup = BeautifulSoup(content)

        try:
            self.main_div = self.soup.select('.main-data-block')[0]
        except:
            raise Exception(_('Shipment not found'))

        error_div = self.soup.find('div', class_='error')
        if error_div:
            raise Exception(_('Shipment not found'))

        self.package_title['package_num'] = package_num

    def parse_package_title(self):
        self.package_title = {}

        try:
            title_divs = self.main_div.select('.hbox')
            status_name = unicode(title_divs[1].find('span', class_='value').string)
            courier_status_obj = self.get_status_instance(status_name)
            self.current_status = courier_status_obj

            date_of_sending = title_divs[2].find('span', class_='value').string
            if date_of_sending:
                self.package_title['date_of_sending'] = datetime.strptime(date_of_sending, "%Y-%m-%d %H:%M:%S")

            delivery_date = title_divs[3].find('span', class_='value').string
            if delivery_date:
                self.package_title['delivery_date'] = datetime.strptime(delivery_date, "%Y-%m-%d %H:%M:%S")
        except:
            raise Exception(_('Import error'))

        return self.package_title

    def parse_status_history(self):
        def data_tr_class(css_class):
            tr_classes = ['odd', 'even']
            return css_class in tr_classes

        try:
            status_rows = self.main_div.find_all(class_=data_tr_class)
            for row in status_rows:
                record = {}
                td_list = row.find_all('td')
                date = td_list[0].string
                time = td_list[1].string
                date_time = date + ' ' + time
                record['date_time'] = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                status_name = unicode(td_list[2].string)
                courier_status_obj = self.get_status_instance(status_name)
                record['status'] = courier_status_obj
                record['comments'] = unicode(td_list[3].string)
                record['location'] = unicode(td_list[4].string)
                record['additional_info'] = unicode(td_list[5].string)
                self.status_history.append(record)

                if record['date_time'] > self.current_datetime:
                    self.current_datetime = record['date_time']
                    self.current_status = record['status']
        except:
            raise Exception(_('Import error'))

        self.package_title['current_status'] = self.current_status
        return self.status_history




