from django.conf.urls import url
from .views import WeatherView

urlpatterns = [
    url(r'^poi/(?P<poi__pk>\d+)/$', WeatherView.as_view(), name='weather-api'),
]
