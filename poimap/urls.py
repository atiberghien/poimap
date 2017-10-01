from django.conf.urls import url
from .views import *

urlpatterns = [

    url(r'^api/area/(?P<slug>[\w-]+)/$', AreaView.as_view(), name='api-area'),
    url(r'^api/area/(?P<slug>[\w-]+)/paths/$', AreaPathsView.as_view(), name='api-area-paths'),
    url(r'^api/area/(?P<slug>[\w-]+)/subpaths/$', SubPathListView.as_view(), name='api-subpath-list'),

    url(r'^api/path/(?P<slug>[\w-]+)/$', PathView.as_view(), name='path-api-detail'),

    url(r'^api/poi/(?P<pk>\d+)/$', POIList.as_view(), name='poi-api-detail'),

    url(r'^api/path/(?P<path_pk>\d+)/poi/list/$', POIList.as_view(), name='api-poi-list'),
    url(r'^api/poi/list/$', POIList.as_view(), name='api-poi-list'),


    url(r'^poi/(?P<pk>\d+)/convert/(?P<to_model>\w+)$', convert_poi, name='convert-poi'),
    url(r'^(?P<area_slug>[\w-]+)/$', MapView.as_view(), name='map'),
]
