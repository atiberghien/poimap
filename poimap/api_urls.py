from django.conf.urls import url
from .views import AreaView, AreaPathsView, SubPathListView, PathView, POIList, POIView

urlpatterns = [
    url(r'^area/(?P<slug>[\w-]+)/$', AreaView.as_view(), name='api-area'),
    url(r'^area/(?P<slug>[\w-]+)/paths/$', AreaPathsView.as_view(), name='api-area-paths'),
    url(r'^area/(?P<slug>[\w-]+)/subpaths/$', SubPathListView.as_view(), name='api-subpath-list'),

    url(r'^path/(?P<slug>[\w-]+)/$', PathView.as_view(), name='path-api-detail'),

    url(r'^poi/(?P<pk>\d+)/$', POIView.as_view(), name='poi-api-detail'),

    url(r'^path/(?P<path_pk>\d+)/poi/list/$', POIList.as_view(), name='api-poi-list'),
    url(r'^poi/list/$', POIList.as_view(), name='api-poi-list'),
]
