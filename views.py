from django.shortcuts import render
from django.views.generic import ListView
from .models import Base, POI


def test(request):
    bases = Base.objects.all()
    return render(request, 'itinerary.html',{'bases': bases})


class POIMapView(ListView):
    model = POI
    template_name = "poi_map.html"
