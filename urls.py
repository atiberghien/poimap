from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from . import views
from views import *

urlpatterns = [
    url(r'^create/$', views.test, name='itinerary_create'),
    # url(r'^detail/(?P<pk>[0-9]+)/$', HostingDetailView.as_view(), name='hosting_detail'),
    # url(r'^list/$', HostingListView.as_view(), name='hosting_list'),
    # url(r'^map/$', HostingMapView.as_view(), name='hosting_map'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
