from django.conf.urls import url
from .views import POIMapView, POIList, TypedPOIListView

urlpatterns = [
    url(r'^map/$', POIMapView.as_view(), name='poi_map'),
    url(r'^rest/poi/(?P<pk>\d+)/$', POIList.as_view(), name='poi-rest-detail'),
    url(r'^rest/poi/list/$', POIList.as_view(), name='poi-rest-list'),
    url(r'^rest/poi/typed/list/$', TypedPOIListView.as_view(), name='typed-poi-rest-list'),
]
