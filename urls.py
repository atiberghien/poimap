from django.conf.urls import url
from .views import POIMapView

urlpatterns = [
    url(r'^map/$', POIMapView.as_view(), name='poi_map'),
]
