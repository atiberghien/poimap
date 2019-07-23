# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.utils.text import slugify
from geopy.geocoders import GoogleV3
from poimap.models import POIType
from transportation.models import Service, TimeSlot
import csv
from datetime import datetime

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--import', dest='import', action="store_true")
        parser.add_argument('--export', dest='export', action="store_true")

    def handle(self, *args, **options):

        if options["import"] and options["export"]:
            print("Only once of these arguments at a time : --import or --export")
            return
        if options["import"]:
            TimeSlot.objects.all().update(hour=None)

            with open('data/horaires.csv') as csvfile:
                reader = csv.reader(csvfile, delimiter="|", quotechar='"')
                for row in reader:
                    service_name = row[0].decode('utf-8')
                    service_name_slug = slugify(service_name)
                    service = Service.objects.get(slug=service_name_slug)
                    i = 1
                    for slot in service.timeslots.all():
                        if row[i]:
                            slot.hour = datetime.strptime(row[i], "%H:%M").time()
                            slot.save()
                        i += 1

        elif options["export"]:
            pass
            # csv.register_dialect('troucelier', delimiter='|', quoting=csv.QUOTE_MINIMAL)
            # with open('data/export/services.csv', 'wb') as f:
            #     writer = csv.writer(f, 'troucelier')
            #     for line in Line.objects.all():
            #         for route in line.routes.all():
            #             for service in route.services.all():
            #                 writer.writerow([line.name.encode('utf-8'),
            #                                  route.name.encode('utf-8'),
            #                                  service.name.encode('utf-8'),
            #                                  service.frequency_label.encode('utf-8')])
        else:
            print("Missing argument --import or --export")
            return
