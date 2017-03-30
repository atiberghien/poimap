from django.conf.urls import url
from .views import HostingCreateView, HostingDetailView, HostingListView

urlpatterns = [
    url(r'^create/$', HostingCreateView.as_view(), name='hosting_create'),
    url(r'^detail/(?P<pk>[0-9]+)/$', HostingDetailView.as_view(), name='hosting_detail'),
    url(r'^list/$', HostingListView.as_view(), name='hosting_list'),
]
