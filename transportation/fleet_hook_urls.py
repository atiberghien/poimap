from django.conf.urls import url
from .views import TransportationFleet, TransportationFleetVehicule

urlpatterns = [
    url(r'^$', TransportationFleet.as_view(), name='transportation-fleet'),
    url(r'^(?P<slug>[\w-]+)/$', TransportationFleetVehicule.as_view(), name='transportation-fleet-vehicule'),

]
