# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from transportation.models import Route, GraphEdge
import googlemaps


class Command(BaseCommand):

    def handle(self, *args, **options):
        gmaps = googlemaps.Client("AIzaSyAAfExuSQBQ9uZ7zrvxKljLw8QnysvfBDs")
        routes = Route.objects.all()
        for route in routes:
            stops = route.get_stops()
            stop_slugs = list(stops.values_list("slug", flat=True))
            for stop1_slug in stop_slugs:
                for stop2_slug in stop_slugs:
                    if stop_slugs.index(stop2_slug) > stop_slugs.index(stop1_slug):
                        stop1 = stops.get(slug=stop1_slug)
                        stop2 = stops.get(slug=stop2_slug)
                        edge, created = GraphEdge.objects.get_or_create(stop1=stop1, stop2=stop2)
                        if created:
                            matrix = gmaps.distance_matrix(stop1.coords, stop2.coords)
                            edge.distance = int(matrix["rows"][0]["elements"][0]["distance"]["value"])
                            edge.save()
                        edge.routes.add(route)
