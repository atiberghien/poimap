from django.conf.urls import url
from .api_views import StopListView, LineListView, api_route_timetable
from .api_views import api_itinerary, api_bus_blueprint, api_driver_service
from .api_views import api_session

urlpatterns = [
    url(r'^stop/list$', StopListView.as_view(), name='api-stop-list'),
    url(r'^line/list$', LineListView.as_view(), name='api-line-list'),
    url(r'^service/list$', api_route_timetable, name='api-route-timetable'),
    url(r'^itinerary$', api_itinerary, name='api-itinerary'),
    url(r'^bus/blueprint$', api_bus_blueprint, name='api-bus-blueprint'),
    url(r'^driver/services$', api_driver_service, name='api-driver-services'),
    url(r'^session/$', api_session, name='api-session'),
]
