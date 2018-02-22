from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.views.generic import TemplateView, DetailView
from django.shortcuts import redirect, get_object_or_404, render
from rest_framework import generics
from shapely.geometry import box
from shapely.affinity import scale
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import PathSerializer, POISerializer, AreaSerializer
from .models import Path, POI, Area
from .forms import CustomItineraryForm

if "hostings" in settings.INSTALLED_APPS:
    from hostings.models import Hostings

import json
import math


class AreaView(generics.RetrieveAPIView):
    queryset = Area.objects.all()
    lookup_field = 'slug'
    serializer_class = AreaSerializer


class PathView(generics.RetrieveAPIView):
    queryset = Path.objects.all()
    lookup_field = 'slug'
    serializer_class = PathSerializer


class SubPathListView(generics.ListAPIView):
    serializer_class = PathSerializer

    def get_queryset(self):
        area = get_object_or_404(Area, slug=self.kwargs["slug"])
        root_path = Path.get_root_nodes().get(geom__within=area.geom)
        return root_path.get_descendants()


class AreaPathsView(generics.ListAPIView):
    serializer_class = PathSerializer

    def get_queryset(self):
        area = get_object_or_404(Area, slug=self.kwargs["slug"])

        ## FIXME
        return Path.objects.all()


        queryset = Path.objects.filter(geom__within=area.geom)
        bbox_param = self.request.query_params.get('bbox', None)
        if bbox_param:
            bbox_param = [float(x) for x in bbox_param.split(',')]
            xmin = bbox_param[0]
            ymin = bbox_param[1]
            xmax = bbox_param[2]
            ymax = bbox_param[3]
            bbox = Polygon.from_bbox((xmin, ymin, xmax, ymax))
            queryset = queryset.filter(geom__contained=bbox)
        return queryset


class POIDetailView(DetailView):
    model = POI


class POIView(generics.RetrieveAPIView):
    queryset = POI.objects.all()
    serializer_class = POISerializer

class POIList(generics.ListAPIView):
    serializer_class = POISerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = {
        'type__slug': ['exact', 'in'],
    }

    def get_queryset(self):
        queryset = POI.objects.all()

        path_pk = self.request.query_params.get('path_pk', None)
        if path_pk:
            path = get_object_or_404(Path, id=path_pk)
            queryset = queryset.filter(geom__distance_lte=(path.geom, D(km=2)))
        else:
            bbox_param = self.request.query_params.get('bbox', None)
            if bbox_param:
                bbox_param = [float(x) for x in bbox_param.split(',')]
                xmin = bbox_param[0]
                ymin = bbox_param[1]
                xmax = bbox_param[2]
                ymax = bbox_param[3]
                bbox = Polygon.from_bbox((xmin, ymin, xmax, ymax))
                queryset = queryset.filter(geom__contained=bbox)

        return queryset

class MapView(TemplateView):
    template_name = "map.html"

    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)
        area = Area.objects.first()
        if "area_slug" in kwargs:
            area = Area.objects.get(slug=kwargs["area_slug"])
        context.update({
            'area' : area,
            'form' : CustomItineraryForm()
        })
        return context



def custom_itinerary(request, path_slug):
    path = Path.objects.get(slug=path_slug)
    form = CustomItineraryForm(request.POST)
    form.is_valid()
    data = form.cleaned_data
    start = data["start_point"].coords
    end = data["end_point"].coords
    bbox = box(start["lng"], start["lat"], end["lng"], end["lat"])
    bbox = scale(bbox, xfact=1.1, yfact=1.1)
    bbox = Polygon(list(bbox.exterior.coords))
    custom_path = path.geom.intersection(bbox)
    custom_path.transform(3035)
    length = custom_path.length / 1000
    custom_path.transform(4326)

    step = data["step"]*1000
    step_cpt = 1
    margin = 5000
    qs = POI.objects.filter(geom__within=bbox)
    if "hostings" in settings.INSTALLED_APPS:
        qs = qs.instance_of(Hostings)
    for poi in qs:
        print step_cpt*step-margin, poi.distance ,step_cpt*step+margin
        if poi.distance >= step_cpt*step-margin and poi.distance <= step_cpt*step+margin:
            print "youpi"
        step_cpt += 1
        # for x in range():


    return render(request, "itinerary.html", {
        "step" : data["step"]*1000,
        "margin" : 5000,
        "path_slug" : path_slug,
        "poi_list" : POI.objects.filter(geom__within=bbox),
        "total_length" : length,
    })

@login_required
@staff_member_required
def convert_poi(request, pk, to_model):
    poi = POI.objects.get(id=pk)
    target_ct = ContentType.objects.get(model=to_model)
    target = target_ct.model_class().objects.create(poi_ptr_id=poi.id, name=poi.name, type=poi.type, geom=poi.geom)
    return redirect("admin:%s_%s_change" % (target_ct.app_label, target_ct.model), target.id)
