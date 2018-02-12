from django.conf.urls import url
from .views import HostingCreateView, HostingDetailView, HostingListView

urlpatterns = [
    url(r'^$', HostingListView.as_view(), name='hosting_list'),
    url(r'^(?P<slug>[\w-]+)/$', HostingDetailView.as_view(), name='hosting_detail'),
]
