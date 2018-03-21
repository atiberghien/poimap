from django.conf.urls import url
from .views import custom_itinerary

urlpatterns = [
    url(r'^(?P<path_slug>[\w-]+)/itinerary/$', custom_itinerary, name='itinerary'),
]
