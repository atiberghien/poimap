from django.conf.urls import url, include
from django.views.generic import TemplateView
from .views import MapView, LineDetailView, LineListView, StopListView, StopAutocomplete, TransportationItinerary

urlpatterns = [
    url(r'^$', TransportationItinerary.as_view(), name='transportation-itinerary'),
]
