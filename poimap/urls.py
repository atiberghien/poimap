from django.conf.urls import url
from .views import convert_poi, POIDetailView

urlpatterns = [
    url(r'^poi/(?P<pk>\d+)/convert/(?P<to_model>\w+)$', convert_poi, name='convert-poi'),
    url(r'^poi/(?P<pk>\d+)/$', POIDetailView.as_view(), name='poi-detail'),
]
