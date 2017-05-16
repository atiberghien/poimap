from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView
from django.shortcuts import redirect
from django.urls import reverse

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

@login_required
@staff_member_required
def convert_poi(request, pk, to_model):
    poi = POI.objects.get(id=pk)
    target_ct = ContentType.objects.get(model=to_model)
    target = target_ct.model_class().objects.create(poi_ptr_id=poi.id, name=poi.name, type=poi.type, geom=poi.geom)
    return redirect("admin:%s_%s_change" % (target_ct.app_label, target_ct.model), target.id)
