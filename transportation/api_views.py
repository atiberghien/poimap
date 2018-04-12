from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from datetime import datetime, date, timedelta
from dateutil.rrule import rrulestr
from dateutil.tz import tzutc

from networkx.algorithms.shortest_paths.generic import all_shortest_paths

from .serializers import StopSerializer, LineSerializer
from .models import Stop, Line, Route, Service, GraphEdge
from .utils import has_all_stop, get_route_length, get_total_time, increasing_hours, timetable_sort_func, get_max_wait

import pandas as pd
import networkx as nx
import itertools

class StopListView(generics.ListAPIView):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer


class LineListView(generics.ListAPIView):
    queryset = Line.objects.all()
    serializer_class = LineSerializer


@api_view(http_method_names=['GET'])
def api_route_timetable(request):
    route_id = request.GET.get('route_id', None)
    freq_re = request.GET.get('freq_re', None)
    date = request.GET.get('date', None)

    if not route_id:
        return Response({"message": "Route ID is mandatory"})

    result = {
        "columns" : [],
        "rows" : [],
        "values" : [],
        "notes" : [],
    }
    dataset = {}

    route = Route.objects.get(id=route_id)
    stop_names = list(route.get_stops().values_list('name', flat=True))
    services = Service.objects.filter(route=route)
    if date:
        service_ids = []
        for s in services.filter(recurrences__isnull=False):
            rruleset = rrulestr(s.recurrences)
            dt = datetime.strptime(date, "%d/%m/%y").replace(tzinfo=tzutc())
            if dt in rruleset:
                service_ids.append(s.id)
        if service_ids:
            services = Service.objects.filter(id__in=service_ids)
    elif freq_re:
        services = services.filter(frequency_label__regex=freq_re)

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
    return Response(result)

@api_view(http_method_names=['GET'])
def api_itinerary(request):
    source = request.GET.get("source", None)
    target = request.GET.get("target", None)
    travel_date = request.GET.get("travel_date", None)
    traveler_count = request.GET.get("traveler_count", 1)
    travel_unit_price = 1

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
                            distance = GraphEdge.objects.get(stop1__slug=stop1, stop2__slug=stop2)
                            g.add_edge(stop1, stop2, weight=distance)
        try:
            timetables = []
            for path in all_shortest_paths(g, source, target):
                connections = []
                for i in range(len(path)-1):
                    connections.append(list(GraphEdge.objects.get(stop1__slug=path[i], stop2__slug=path[i+1]).routes.values_list('id', flat=True)))
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
                timetable_data = {}
                if len(timetable):
                    timetable_data["total_time"] = timedelta(seconds=get_total_time(timetable)).seconds
                    timetable_data["max_wait"] = timedelta(seconds=get_max_wait(timetable)).seconds
                    timetable_data["length"] = get_route_length(timetable)
                    timetable_data["connexion_count"] = len(timetable)/2 - 1
                    timetable_data["traveler_count"] = traveler_count
                    timetable_data["travel_unit_price"] = travel_unit_price
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
                        current_service_name = timeslot.service.name

                    timetable_data["timeslots"].append(timeslot_data)
                result["timetables"].append(timetable_data)

        except:
            result["success"] = "KO"
            result["msg"] = "Errors during algorith execution"
    else:
        result["success"] = "KO"
        result["msg"] = "Missing input data"
    return Response(result)
