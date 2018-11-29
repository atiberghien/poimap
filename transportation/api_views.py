from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics

from datetime import datetime, date, timedelta
from dateutil.rrule import rrulestr
from dateutil.tz import tzutc

from networkx.algorithms.shortest_paths.generic import all_shortest_paths

from .serializers import StopSerializer, LineSerializer
from .models import Stop, Line, Route, Service, Travel, Ticket, Connection
from .utils import has_all_stop, get_route_length, get_total_time, increasing_hours, timetable_sort_func, get_max_wait, get_travel_price

import pandas as pd
import networkx as nx
import itertools
import time

class StopListView(generics.ListAPIView):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer


class LineListView(generics.ListAPIView):
    queryset = Line.objects.all()
    serializer_class = LineSerializer

    @method_decorator(cache_page(60*60))
    def dispatch(self, *args, **kwargs):
        return super(LineListView, self).dispatch(*args, **kwargs)


def compute_timetable(route_id, freq_re=None, date=None):
    result = {
        "columns" : [],
        "rows" : [],
        "values" : [],
        "notes" : [],
    }
    dataset = {}

    route = Route.objects.get(id=route_id)
    stop_names = list(route.get_stops().values_list('name', flat=True))
    services = Service.objects.filter(is_active=True, route=route)
    if date:
        service_ids = []
        for service in services.filter(recurrences__isnull=False):
            dt = datetime.strptime(date, "%d/%m/%Y").replace(tzinfo=tzutc())
            if dt in service.rruleset:
                service_ids.append(service.id)
        if service_ids:
            services = Service.objects.filter(id__in=service_ids)
        else:
            services = []
    elif freq_re:
        services = services.filter(frequency_label__regex=freq_re)
    else:
        services = services.filter(is_temporary=False)
    note_nb = 1
    for service in services:
        col_data = {
            "name" : service.name,
            "frequency_label" : service.frequency_label
        }
        if service.notes:
            col_data["note_nb"] = note_nb
            note_nb += 1
            result["notes"].append(service.notes)
        result["columns"].append(col_data)

        dataset[service.name] = [t.strftime("%H:%M") if t else "-" for t in service.timeslots.values_list("hour", flat=True)]
    df = pd.DataFrame(dataset, index=stop_names)
    for index, row in df.iterrows():
        result["rows"].append({
            "label" : index,
            "values" : list(row.values)
        })
    return result

@api_view(http_method_names=['GET'])
def api_route_timetable(request):
    route_id = request.GET.get('route_id', None)
    freq_re = request.GET.get('freq_re', None)
    date = request.GET.get('date', None)

    if not route_id:
        return Response({"message": "Route ID is mandatory"})

    
    return Response(compute_timetable(route_id, freq_re=freq_re, date=date))

@api_view(http_method_names=['GET'])
def api_itinerary(request):
    source = request.GET.get("source", None)
    target = request.GET.get("target", None)
    travel_date = request.GET.get("travel_date", None)
    traveler_count = request.GET.get("traveler_count", 1)
    from_time = request.GET.get("from_time", None)
    if from_time:
        from_time = datetime.strptime(from_time, "%H:%M").time()
    go_date = request.GET.get("go_date", None)
    if go_date:
        go_date = datetime.strptime(go_date, "%d/%m/%y").date()
    
    result = {
        "success" : "OK",
        "timetables" : []
    }
    if source and target and travel_date:
        travel_date = datetime.strptime(travel_date, "%d/%m/%y").replace(tzinfo=tzutc())
        routes = Route.objects.all()
        g = nx.DiGraph()
        edges = {}
        for route in routes:
            stop_slugs = list(route.get_stops().values_list("slug", flat=True))
            for stop1 in stop_slugs:
                for stop2 in stop_slugs:
                    if stop_slugs.index(stop2) > stop_slugs.index(stop1):
                        edge = (stop1, stop2)
                        if edge in edges.keys():
                            edges[edge].append(route.id)
                        else:
                            edges[edge] = [route.id]
                            distance = Travel.objects.get(stop1__slug=stop1, stop2__slug=stop2).distance
                            g.add_edge(stop1, stop2, weight=distance)
        try:
            timetables = []
            for path in all_shortest_paths(g, source, target):
                connections = []
                for i in range(len(path)-1):
                    connections.append(list(Travel.objects.get(stop1__slug=path[i], stop2__slug=path[i+1]).routes.values_list('id', flat=True)))
                connections = itertools.product(*connections)
                for connection in connections:
                    all_services = []
                    for route_id in connection:
                        route = Route.objects.get(id=route_id)
                        available_route_services = []
                        for service in route.services.all():
                            if travel_date is None or travel_date in service.rruleset:
                                available_route_services.append(service)
                        all_services.append(available_route_services)
                    service_combinaisons = itertools.product(*all_services)

                    for service_combinaison in service_combinaisons:
                        i = 0
                        timetable = []
                        for service in service_combinaison:
                            start_timeslot = service.timeslots.get(stop__slug=path[i])
                            end_timeslot = service.timeslots.get(stop__slug=path[i+1])
                            timetable.append(start_timeslot)
                            timetable.append(end_timeslot)
                            i+=1
                        timetables.append(timetable)

            timetables = filter(has_all_stop, timetables)
            timetables = filter(increasing_hours, timetables)
            timetables.sort(key=timetable_sort_func)


            for timetable in timetables:
                if go_date and from_time:
                    if travel_date.date() == go_date and from_time > timetable[0].hour:
                        continue
                timetable_data = {}
                if len(timetable):
                    timetable_data["total_time"] = timedelta(seconds=get_total_time(timetable)).seconds
                    timetable_data["max_wait"] = timedelta(seconds=get_max_wait(timetable)).seconds
                    timetable_data["length"] = get_route_length(timetable)
                    timetable_data["connexion_count"] = len(timetable)/2 - 1
                    timetable_data["traveler_count"] = traveler_count
                    timetable_data["travel_unit_price"] = get_travel_price(timetable)
                    timetable_data["timeslots"] = []
                current_service_name = None
                for timeslot in timetable:
                    timeslot_data = {
                        "stop_id" : timeslot.stop.id,
                        "stop_name" : timeslot.stop.name,
                        "hour" : datetime.combine(date.today(), timeslot.hour).strftime("%H:%M")
                    }
                    if timeslot.service.name != current_service_name:
                        timeslot_data["service_name"] = timeslot.service.name
                        timeslot_data["service_slug"] = timeslot.service.slug
                        current_service_name = timeslot.service.name

                    timetable_data["timeslots"].append(timeslot_data)
                result["timetables"].append(timetable_data)

        except:
            result["success"] = "KO"
            result["msg"] = "ALGO_ERROR"
    else:
        result["success"] = "KO"
        result["msg"] = "MISSING_INPUT_DATA"
    if len(result["timetables"])== 0 :
        result["success"] = "KO"
        result["msg"] = "NO_RESULT"
    return Response(result)


def _find_booked_seats(service, travel_date, travel_info):
    seats = []
    if travel_info["departure_date"] == travel_date.strftime("%d/%m/%y"):
        for traveller in travel_info["travellers"]:
            if "seats" in traveller:
                for service_slug, seat_nb in traveller["seats"].iteritems():
                    if service_slug == service.slug:
                        seats.append(seat_nb)
    return seats

@api_view(http_method_names=['GET'])
def api_bus_blueprint(request):
    travel_date = request.GET.get("travel_date", None)
    service_slug = request.GET.get("service_slug", None)
    result = {}
    if travel_date and service_slug:
        travel_date = datetime.strptime(travel_date, "%d/%m/%y").replace(tzinfo=tzutc())
        service = Service.objects.get(slug=service_slug)
        bus = service.bus_set.first()
        result["blueprint"] = open(bus.blueprint.path).read()

        booked_seats = list(Connection.objects.filter(ticket__date=travel_date.date(), service=service).values_list('seat', flat=True))

        if "travels" in request.session:
            travels = request.session["travels"]
            for travel in travels:
                booked_seats.extend(_find_booked_seats(service, travel_date, travel["go"]))
                if travel["return"]:
                    booked_seats.extend(_find_booked_seats(service, travel_date, travel["return"]))
        result["booked_seats"] = booked_seats
    return Response(result)

@api_view(http_method_names=['GET'])
def api_driver_service(request):
    service_name = request.GET.get("service_name", None)
    result = []
    today = date.today()
    connections = Connection.objects.filter(ticket__date__gte=today, ticket__order__paid_at__isnull=False)
    if service_name:
        connections = connections.filter(service__name__icontains=service_name)
    
    service_ids = set(connections.values_list("service__id", flat=True))
    for service_id in service_ids:
        service = Service.objects.get(id=service_id)
        dates = list(connections.filter(service=service).order_by('ticket__date').values_list("ticket__date", flat=True))
        dates = set([d.strftime("%d/%m/%y") for d in dates])
        result.append({
            "name" : service.name,
            "slug" : service.slug,
            "description" : str(service.route).decode("utf-8"),
            "dates" : dates
        })
    return Response(result)


@api_view(http_method_names=['GET'])
def api_session(request):
    return Response(request.session["travels"])