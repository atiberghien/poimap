from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import StopSerializer, LineSerializer
from .models import Stop, Line, Route, Service
import pandas as pd

class StopListView(generics.ListAPIView):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer


class LineListView(generics.ListAPIView):
    queryset = Line.objects.all()
    serializer_class = LineSerializer


@api_view(http_method_names=['GET'])
def api_route_timetable(request):
    route_id = request.GET.get('route_id', None)

    if not route_id:
        return Response({"message": "Route ID is mandatory"})

    result = {
        "columns" : [],
        "rows" : [],
        "values" : []
    }
    dataset = {}

    route = Route.objects.get(id=route_id)
    stop_names = list(route.get_stops().values_list('name', flat=True))
    for service in Service.objects.filter(route=route):
        result["columns"].append({
            "name" : service.name,
            "frequency_label" : service.frequency_label
        })
        dataset[service.name] = [t.strftime("%H:%M") if t else "-" for t in service.timeslots.values_list("hour", flat=True)]
    df = pd.DataFrame(dataset, index=stop_names)
    for index, row in df.iterrows():
        result["rows"].append({
            "label" : index,
            "values" : list(row.values)
        })
    return Response(result)
