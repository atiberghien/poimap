from django.shortcuts import render
from django.views.generic import ListView
from .models import Base, POI


class POIMapView(ListView):
    model = POI
    template_name = "poi_map.html"
