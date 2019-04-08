from django.conf.urls import url, include
from django.views.generic import TemplateView
from .views import StopAutocomplete
from .views import TransportationTicketRecovery, TransportationTicket
from .views import TransportationTicketPrintView, TransportationTicketValidation
from .views import TransportationOrderInvoice, TransportationOrderInvoicePrintView 
from .views import DriverView, DriverDailyService, DriverDailyServicePrintView
from .views import ServiceTimeTablePrintView, ServiceTimeTableView, line_prices_pdf
from .views import travels_csv, stops_csv, ProfessionnalLoginView, ProfessionnalAccessView
from .views import SMSNotificationSubscription, SMSAnnouncementView


urlpatterns = [
    url(r'^stops/autocomplete/$', StopAutocomplete.as_view(), name="stop-autocomplete"),
    url(r'^service/pdf/$', ServiceTimeTablePrintView.as_view(), name='route-timetable-pdf'),
    url(r'^line/prices/pdf/$', line_prices_pdf, name='line-prices-pdf'),
    url(r'^service/$', ServiceTimeTableView.as_view(), name='route-timetable'),
    url(r'^ticket/recovery/$', TransportationTicketRecovery.as_view(), name='ticket-recovery'),
    url(r'^order/(?P<num>[\w-]+)/invoice/$', TransportationOrderInvoice.as_view(), name='ticket-order-invoice'),
    url(r'^order/(?P<num>[\w-]+)/invoice/pdf/$', TransportationOrderInvoicePrintView.as_view(), name='ticket-order-invoice-pdf'),
    url(r'^ticket/(?P<num>[\w-]+)/$', TransportationTicket.as_view(), name='ticket'),
    url(r'^ticket/(?P<num>[\w-]+)/pdf/$', TransportationTicketPrintView.as_view(), name='ticket-pdf'),
    url(r'^ticket/(?P<num>[\w-]+)/validate/$', TransportationTicketValidation.as_view(), name='ticket-validation'),
    
    url(r'^sms/subscribe/$', SMSNotificationSubscription.as_view(), name='sms-subscription'),

    url(r'^pro/$', ProfessionnalAccessView.as_view(), name='pro-access'),
    url(r'^pro/login/$', ProfessionnalLoginView.as_view(), name='login-pro'),
    url(r'^pro/driver/$', DriverView.as_view(), name='driver'),
    url(r'^pro/driver/service/pdf/$', DriverDailyServicePrintView.as_view(), name='driver-daily-service-pdf'),
    url(r'^pro/sms/announcement/$', SMSAnnouncementView.as_view(), name='sms-announcement'),
    
    
    url(r'^travels\.csv$', travels_csv, name='travels-csv'),
    url(r'^stops\.csv$', stops_csv, name='stops-csv'),
]
