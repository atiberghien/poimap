from django.views.generic import ListView
from rest_framework import generics
from .serializers import POISerializer, TypedPOISerializer
from .models import POI, POIType


class POIMapView(ListView):
    model = POI
    template_name = "poi_map.html"

class TypedPOIListView(generics.ListAPIView):
    queryset = POIType.objects.all()
    serializer_class = TypedPOISerializer

class POIList(generics.ListAPIView):
    serializer_class = POISerializer

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return POI.objects.filter(id=self.kwargs['pk'])
        return POI.objects.all()
