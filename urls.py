from django.conf.urls import url
from .views import test, POIMapView

urlpatterns = [
    url(r'^create/$', test, name='itinerary_create'),
    url(r'^map/$', POIMapView.as_view(), name='poi_map'),
]
