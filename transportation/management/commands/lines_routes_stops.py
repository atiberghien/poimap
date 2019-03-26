# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.utils.text import slugify
from geopy.geocoders import GoogleV3
from poimap.models import POIType
from transportation.models import Line, Route, RouteStop, Stop
import csv

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--import', dest='import', action="store_true")
        parser.add_argument('--export', dest='export', action="store_true")

    def handle(self, *args, **options):
        if options["import"] and options["export"]:
            print "Only one of these arguments at a time : --import or --export"
            return
        if options["import"]:
            bus_type = POIType.objects.get_or_create(label=u"Arrêt de bus", icon='bus')[0]

            Line.objects.all().delete()
            Route.objects.all().delete()
            RouteStop.objects.all().delete()
            Stop.objects.all().delete()
            stop_order = 0

            with open('data/lignes_sens_arrets.csv') as csvfile:
                reader = csv.reader(csvfile, delimiter="|", quotechar='"')
                for row in reader:
                    line_name, route_name, stop_name, latitude, longitude= row
                    line_name = line_name.decode('utf-8')
                    route_name = route_name.decode('utf-8')
                    stop_name = stop_name.decode('utf-8')
                    line_name_slug = slugify(line_name)
                    route_name_slug = slugify(route_name)
                    stop_name_slug = slugify(stop_name)
                    try:
                        line = Line.objects.get(slug=line_name_slug)
                    except Line.DoesNotExist:
                        line = Line.objects.create(name=line_name)
                    assert line.slug == line_name_slug

                    try:
                        route = Route.objects.get(line=line, slug=route_name_slug)
                        stop_order += 1
                    except Route.DoesNotExist:
                        if Route.objects.filter(line=line, direction="1").exists():
                            route = Route.objects.create(name=route_name, line=line, direction="2")
                        else:
                            route = Route.objects.create(name=route_name, line=line, direction="1")
                        stop_order = 0
                    assert route.slug == route_name_slug

                    try:
                        stop = Stop.objects.get(slug=stop_name_slug)
                    except Stop.DoesNotExist:
                        geom = GEOSGeometry('POINT (%s %s 0)' % (longitude, latitude))
                        stop = Stop.objects.create(name=stop_name, description="N/C", type=bus_type, geom=geom)
                    RouteStop.objects.get_or_create(route=route, stop=stop, order=stop_order)
                    assert stop.slug == stop_name_slug
        elif options["export"]:
            csv.register_dialect('troucelier', delimiter='|', quoting=csv.QUOTE_MINIMAL)
            with open('data/export/lignes_sens_arrets.csv', 'wb') as f:
                writer = csv.writer(f, 'troucelier')
                for line in Line.objects.all():
                    for route in line.routes.all():
                        for route_stop in RouteStop.objects.filter(route=route):
                            writer.writerow([line.name.encode('utf-8'),
                                             route.name.encode('utf-8'),
                                             route_stop.stop.name.encode('utf-8'),
                                             route_stop.stop.geom.coords[1],
                                             route_stop.stop.geom.coords[0]])
        else:
            print "Missing argument --import or --export"
            return
