from django.conf.urls import url, include
from django.views.generic import TemplateView
from .views import StopAutocomplete
from .views import TransportationTicketRecovery, TransportationTicket
from .views import TransportationTicketPrintView, TransportationTicketValidation
from .views import TransportationOrderInvoice, TransportationOrderInvoicePrintView

urlpatterns = [
    url(r'^arrets/autocomplete/$', StopAutocomplete.as_view(), name="stop-autocomplete"),
    url(r'^ticket/recovery/$', TransportationTicketRecovery.as_view(), name='ticket-recovery'),
    url(r'^order/(?P<num>[\w-]+)/invoice/$', TransportationOrderInvoice.as_view(), name='ticket-order-invoice'),
    url(r'^order/(?P<num>[\w-]+)/invoice/pdf/$', TransportationOrderInvoicePrintView.as_view(), name='ticket-order-invoice-pdf'),
    url(r'^ticket/(?P<num>[\w-]+)/$', TransportationTicket.as_view(), name='ticket'),
    url(r'^ticket/(?P<num>[\w-]+)/pdf/$', TransportationTicketPrintView.as_view(), name='ticket-pdf'),
    url(r'^ticket/(?P<num>[\w-]+)/validate/$', TransportationTicketValidation.as_view(), name='ticket-validation'),
]
