# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils.translation import ugettext_lazy as _
from couriers.modules import CourierBaseModule
from couriers.models import Courier
from bs4 import BeautifulSoup
from datetime import datetime
from mechanize import Browser


class CourierManager(CourierBaseModule):
    def __init__(self, package_num, courier=None):
        super(CourierManager, self).__init__(package_num, courier)

        pack_num_verification(package_num)

        url = 'https://poland.fedex.com/domestic-shipping/pub/tracktrace.do'
        if self.courier.url:
            url = self.courier.url

        try:
            br = Browser()
            br.open(url)
            br.select_form(name="formTrackTrace")
            br['packageId'] = str(self.package_num)
            br.submit()
            content = br.response().read()
        except:
            raise IOError(_('Courier server is not available. Check the server address.'))

        self.soup = BeautifulSoup(content)

        self.package_title['package_num'] = package_num

    def parse_package_title(self):
        def data_tr_class(css_class):
            tr_classes = ['customContentTableRowEven', 'customContentTableRowOdd']
            return css_class in tr_classes

        try:
            title_block = self.soup.find_all('tr', class_='customContentTable')[2]
        except:
            raise Exception(_('Shipment not found'))

        try:
            title_rows = title_block.find_all(class_=data_tr_class)
            span = title_rows[1].find_all('span')
            self.package_title['sent_from'] = unicode(span[1].string)
            self.package_title['deliver_to'] = unicode(span[3].string)
            span = title_rows[2].find_all('span')
            date_of_sending = unicode(span[1].string)
            if date_of_sending:
                self.package_title['date_of_sending'] = datetime.strptime(date_of_sending, "%d-%m-%Y %H:%M")
            delivery_date = unicode(span[3].string)
            if delivery_date:
                self.package_title['delivery_date'] = datetime.strptime(delivery_date, "%d-%m-%Y")

            span = title_rows[3].find_all('span')
            self.package_title['weight'] = unicode(span[1].string)
            span = title_rows[4].find_all('span')
            self.package_title['size'] = unicode(span[1].string)
        except:
            raise Exception(_('Import error'))

        return self.package_title

    def parse_status_history(self):
        def data_tr_class(css_class):
            tr_classes = ['customContentTableRowEven', 'customContentTableRowOdd']
            return css_class in tr_classes

        try:
            status_history_block = self.soup.find_all('tr', class_='customContentTable')[1]
            status_rows = status_history_block.find_all(class_=data_tr_class)
        except IndexError:
            raise IndexError(_('Undefined status history.'))

        try:
            for row in status_rows:
                record = {}
                values = row.find_all('span')
                date_time = unicode(values[0].string)
                record['date_time'] = datetime.strptime(date_time, "%d-%m-%Y %H:%M")
                status_name = unicode(values[1].string)
                courier_status_obj = self.get_status_instance(status_name)
                record['status'] = courier_status_obj
                record['location'] = unicode(values[2].string)

                self.status_history.append(record)

                if record['date_time'] > self.current_datetime:
                    self.current_datetime = record['date_time']
                    self.current_status = record['status']
        except:
            raise Exception(_('Import error'))

        self.package_title['current_status'] = self.current_status
        return self.status_history

