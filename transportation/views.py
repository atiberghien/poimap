# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, DetailView, ListView
from .models import Line, Stop, Route
from poimap.models import Area
from dal import autocomplete

class MapView(TemplateView):
    template_name = 'transportation/map.html'

    def get_context_data(self):
        context = TemplateView.get_context_data(self)
        context["area"] = Area.objects.first()
        context["lines"] = Line.objects.all()
        return context


class LineDetailView(DetailView):
    model = Line

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        try:
            context["to_route"] = self.get_object().route_set.get(direction=1)
        except Route.DoesNotExist:
            context["to_route"] = None
        try:
            context["from_route"] = self.get_object().route_set.get(direction=2)
        except Route.DoesNotExist:
            context["from_route"] = None

        return context


class LineListView(ListView):
    model = Line


class StopListView(ListView):
    model = Stop
    queryset = Stop.objects.all().order_by('name')
    context_object_name = "stops"

class StopAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Stop.objects.all()
        departure = self.forwarded.get('departure', None)
        if departure:
            qs = qs.exclude(id=departure)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs.order_by('name')

from django.views.generic import View
from django.shortcuts import render
from .forms import SearchServiceForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class TransportationItinerary(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'transportation/itinerary_form.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        template_name = 'transportation/itinerary.html'
        if "timetable" in request.POST:
            timetable = json.loads(request.POST.get('timetable'))
            form_data = {
                "departure" :  timetable["timeslots"][0]["stop_id"],
                "arrival" : timetable["timeslots"][-1]["stop_id"],
                "arrival_date" : timetable["arrival_date"],
                "departure_date" : timetable["departure_date"],
                "nb_passengers" : timetable["traveler_count"],
            }
            if "go" in request.POST:
                context["go"] = request.POST.get('go')
                context["return"] = request.POST.get('go')
                template_name = 'transportation/itinerary_summary.html'
            else:
                context["direction"] = 2
                context["go"] = request.POST.get('timetable')
        else:
            form_data = request.POST
            context["direction"] = 1
        form = SearchServiceForm(form_data)

        if form.is_valid():
            context.update(form.cleaned_data)

        context["search_form"] = form
        return render(request, template_name, context)
