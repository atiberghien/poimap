from django.conf.urls import url
from .views import POIMapView, POIList, TypedPOIListView, convert_poi

urlpatterns = [
    url(r'^map/$', POIMapView.as_view(), name='poi_map'),
    url(r'^poi/(?P<pk>\d+)/convert/(?P<to_model>\w+)$', convert_poi, name='convert-poi'),
    url(r'^rest/poi/(?P<pk>\d+)/$', POIList.as_view(), name='poi-rest-detail'),
    url(r'^rest/poi/list/$', POIList.as_view(), name='poi-rest-list'),
    url(r'^rest/poi/typed/list/$', TypedPOIListView.as_view(), name='typed-poi-rest-list'),
]
