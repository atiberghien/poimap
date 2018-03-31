from django.conf.urls import url, include
from django.views.generic import TemplateView
from .views import MapView, LineDetailView, LineListView, StopListView, StopAutocomplete

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="transportation/base.html"), name='map'),
    url(r'^carte/$', MapView.as_view(), name='map'),
    url(r'^lignes/$', LineListView.as_view(), name="line-list"),
    url(r'^arrets/$', StopListView.as_view(), name="stop-list"),
    url(r'^arrets/autocomplete/$', StopAutocomplete.as_view(), name="stop-autocomplete"),
    url(r'^ligne/(?P<slug>[\w-]+)/$', LineDetailView.as_view(), name="line-detail"),


]
