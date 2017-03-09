from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from . import views
from views import *

urlpatterns = [
    url(r'^create/$', HostingsCreateView.as_view(), name='hostings_create'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
