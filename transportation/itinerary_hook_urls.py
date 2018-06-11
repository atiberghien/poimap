from django.conf.urls import url
from .views import TransportationItinerary, TransportationCart, TransportationCartDeleteItem,\
 TransportationCartSaveTravellers, TransportationCheckout, TransportationCheckoutConfirmation

urlpatterns = [
    url(r'^$', TransportationItinerary.as_view(), name='transportation-itinerary'),
    url(r'^infos/$', TransportationCart.as_view(), name='transportation-summary'),
    url(r'^infos/delete/$', TransportationCartDeleteItem.as_view(), name='transportation-cart-delete-item'),
    url(r'^infos/travellers/$', TransportationCartSaveTravellers.as_view(), name='transportation-add-travellers'),
    url(r'^checkout/(?P<order_num>[\w-]+)/$', TransportationCheckout.as_view(), name='transportation-checkout-payment'),
    url(r'^checkout/$', TransportationCheckout.as_view(), name='transportation-checkout'),
    url(r'^checkout/(?P<order_num>[\w-]+)/confirmation/$', TransportationCheckoutConfirmation.as_view(), name='transportation-checkout-confirmation'),
]
