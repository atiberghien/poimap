from django.conf.urls import url
from .views import convert_poi, POIDetailView, MapView, custom_itinerary

urlpatterns = [
    url(r'^poi/(?P<pk>\d+)/convert/(?P<to_model>\w+)$', convert_poi, name='convert-poi'),
    url(r'^poi/(?P<pk>\d+)/$', POIDetailView.as_view(), name='poi-detail'),
    # url(r'^(?P<area_slug>[\w-]+)/$', MapView.as_view(), name='map'),
    # url(r'^(?P<path_slug>[\w-]+)/itinerary/$', custom_itinerary, name='itinerary'),
    # url(r'^$', MapView.as_view(), name='map-default'),
]
