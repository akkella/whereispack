# -*- coding: utf-8 -*-

from datetime import datetime
from couriers.models import CourierStatus
from packages.models import Package, PackageStatusHistory
from django.utils.translation import ugettext_lazy as _
import importlib


class CourierBaseModule(object):
    def __init__(self, package_num, courier=None):
        self.package_num = package_num
        if courier is None:
            raise FeatureNotFound(_('Courier note found'))
        self.courier = courier
        self.soup = None
        self.current_datetime = datetime.min
        self.current_status = None
        self.package_title = {'courier': self.courier}
        self.status_history = []

    def parse_package_title(self):
        pass

    def parse_status_history(self):
        # TODO Добавить указание признака посылка доставлена или нет
        pass

    def update_package_data(self):
        self.parse_package_title()
        self.parse_status_history()

        package_obj, created = Package.objects.update_or_create(
            courier=self.courier,
            package_num=self.package_num,
            defaults=self.package_title
        )

        for package_status in self.status_history:
            package_status['package'] = package_obj
            status_obj, created = PackageStatusHistory.objects.update_or_create(
                package=package_obj,
                date_time=package_status['date_time'],
                defaults=package_status
            )

        return package_obj

    def get_status_instance(self, status_name):
        updated_values = {'courier': self.courier, 'status_name': status_name}
        courier_status_obj, created = CourierStatus.objects.get_or_create(
            courier=self.courier,
            status_name=status_name,
            defaults=updated_values
        )
        return courier_status_obj


def get_courier_manager(package_num, courier):
    if courier.module is None:
        raise NoModuleException(u"%s" % _("Courier hasn't a export module."))
    try:
        module = importlib.import_module('couriers.modules.' + courier.module)
        courier_manager = module.CourierManager(package_num, courier)
    except AttributeError:
        raise Exception(u"%s" % _('Module is invalid.'))
    return courier_manager


class FeatureNotFound(ValueError):
    pass


class NoModuleException(Exception):
    pass