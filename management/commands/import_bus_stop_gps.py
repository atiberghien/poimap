from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from transportation.models import Stop

import csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('Bus_Stop_GPS.csv', 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter='|', quotechar='"')
            csvreader.next()
            for row in csvreader:
                stop_name, latitude, longitude = row
                stop, created = Stop.objects.get_or_create(name=stop_name)
                stop.gps = Point(float(longitude.replace(',', '.')),
                                 float(latitude.replace(',', '.')))
                stop.save()
