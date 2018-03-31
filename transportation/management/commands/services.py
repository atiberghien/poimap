# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.utils.text import slugify
from geopy.geocoders import GoogleV3
from poimap.models import POIType
from transportation.models import Line, Route, RouteStop, Stop, Service
import csv

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--import', dest='import', action="store_true")
        parser.add_argument('--export', dest='export', action="store_true")

    def handle(self, *args, **options):

        if options["import"] and options["export"]:
            print "Only once of these arguments at a time : --import or --export"
            return
        if options["import"]:
            Service.objects.all().delete()

            with open('data/services.csv') as csvfile:
                reader = csv.reader(csvfile, delimiter="|", quotechar='"')
                for row in reader:
                    line_name, route_name, service_name, frequency_label = row
                    line_name = line_name.decode('utf-8')
                    route_name = route_name.decode('utf-8')
                    service_name = service_name.decode('utf-8')
                    line_name_slug = slugify(line_name)
                    route_name_slug = slugify(route_name)

                    route = Route.objects.get(slug=route_name_slug, line__slug=line_name_slug)
                    Service.objects.create(name=service_name, route=route, frequency_label=frequency_label)
        elif options["export"]:
            csv.register_dialect('troucelier', delimiter='|', quoting=csv.QUOTE_MINIMAL)
            with open('data/export/services.csv', 'wb') as f:
                writer = csv.writer(f, 'troucelier')
                for line in Line.objects.all():
                    for route in line.routes.all():
                        for service in route.services.all():
                            writer.writerow([line.name.encode('utf-8'),
                                             route.name.encode('utf-8'),
                                             service.name.encode('utf-8'),
                                             service.frequency_label.encode('utf-8')])
        else:
            print "Missing argument --import or --export"
            return
