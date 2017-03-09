from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from . import views
from views import *

urlpatterns = [
    url(r'^create/$', HostingCreateView.as_view(), name='hosting_create'),
    url(r'^detail/(?P<pk>[0-9]+)/$', HostingDetailView.as_view(), name='hosting_detail'),
    url(r'^list/$', HostingListView.as_view(), name='hosting_list'),
    url(r'^map/$', HostingMapView.as_view(), name='hosting_map'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
