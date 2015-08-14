# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from couriers.models import Courier
from couriers.modules import CourierBaseModule
from bs4 import BeautifulSoup
import mechanize
from datetime import datetime
import requests
from django.utils.translation import ugettext_lazy as _


class CourierManager(CourierBaseModule):
    def __init__(self, package_num, courier=None):
        super(CourierManager, self).__init__(package_num, courier)

        pack_num_verification(package_num)

        url = "https://www.ppl.cz/main2.aspx?cls=Package&idSearch=%s"
        if self.courier.url:
            url = self.courier.url
        url = url % package_num

        try:
            response = mechanize.urlopen(url)
            html = response.read()
        except:
            raise IOError(_('Courier server is not available. Check the server address.'))

        self.soup = BeautifulSoup(html)

        captions = self.soup.find_all('caption')
        if not captions:
            raise Exception(_('Shipment not found'))

        self.main_div = ''
        for caption in captions:
            if caption.text == u'Informace o zásilce ':
                self.main_div = caption.parent.parent
                break
        if not self.main_div:
            raise Exception(_('Shipment not found'))

        self.content_tables = self.main_div.find_all('table')
        if not self.content_tables:
            raise Exception(_('Import error'))

        self.package_title['package_num'] = package_num

    def parse_package_title(self):
        try:
            title_table = self.content_tables[0]
            tr = title_table.find_all('tr')[1]
            values = tr.find_all('td')
            self.package_title['paid_by_card'] = bool(values[2].text)
            self.package_title['sender'] = values[2].text
            self.package_title['customer_ref'] = values[3].text
            self.package_title['post_code'] = values[4].text
            self.package_title['city'] = values[5].text
            self.package_title['country'] = values[6].text
            self.package_title['weight'] = values[7].text
            self.package_title['cod'] = values[8].text
        except:
            raise Exception(_('Import error'))

        return self.package_title

    def parse_status_history(self):
        try:
            date_table = self.content_tables[1]
            date_time_str = date_table.find_all('td')[2].h2.text
            date_time = datetime.strptime(date_time_str, "%d.%m.%Y %H:%M")
            status_name = self.content_tables[2].find_next_sibling("div").b.text
            courier_status_obj = self.get_status_instance(status_name)
            record = {
                'date_time': date_time,
                'status': courier_status_obj
            }
            self.status_history.append(record)
            self.current_status = courier_status_obj
        except:
            raise Exception(_('Import error'))

        return self.status_history


