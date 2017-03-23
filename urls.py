from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from djgeojson.views import GeoJSONLayerView

from . import views, models
from models import Hostings
from views import *

urlpatterns = [
    url(r'^create/$', HostingCreateView.as_view(), name='hosting_create'),
    url(r'^detail/(?P<pk>[0-9]+)/$', HostingDetailView.as_view(), name='hosting_detail'),
    url(r'^list/$', HostingListView.as_view(), name='hosting_list'),
    url(r'^map/$', HostingMapView.as_view(), name='hosting_map'),
    url(r'^data.geojson$', GeoJSONLayerView.as_view(model=Hostings), name='data')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
