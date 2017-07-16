from django.conf.urls import url
from .views import TransportationView

urlpatterns = [
    url(r'^$', TransportationView.as_view(), name='transportation'),
]
