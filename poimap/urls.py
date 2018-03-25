from django.conf.urls import url
from .views import convert_poi, POIDetailView, POIRatingView

urlpatterns = [
    url(r'^(?P<pk>\d+)/convert/(?P<to_model>\w+)$', convert_poi, name='convert-poi'),
    url(r'^(?P<pk>\d+)/vote/$', POIRatingView.as_view(), name='poi-rating'),
    url(r'^(?P<slug>[\w-]+)/$', POIDetailView.as_view(), name='poi-detail'),
]
