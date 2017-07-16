from django.conf.urls import url
from .api_views import StopListView

urlpatterns = [
    url(r'^stop/list$', StopListView.as_view(), name='api-stop-list'),
]
