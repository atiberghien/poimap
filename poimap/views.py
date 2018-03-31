from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.edit import CreateView
from django.urls import reverse
from django.contrib.gis.measure import D

from django.views.generic import DetailView
from django.shortcuts import redirect, get_object_or_404
from rest_framework import generics
from django.contrib.gis.geos import Polygon
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import PathSerializer, POISerializer, AreaSerializer
from .models import Path, POI, Area, POIRating
from .forms import POIRatingForm

if "hostings" in settings.INSTALLED_APPS:
    from hostings.models import Hostings


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
        try:
            root_path = Path.get_root_nodes().get(geom__within=area.geom)
            return root_path.get_descendants()
        except Path.DoesNotExist:
            return Path.objects.none()


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

    def get_context_data(self, **kwargs):
        context = super(POIDetailView, self).get_context_data(**kwargs)
        context["voting_form"] = POIRatingForm(initial={"poi" : self.get_object(), "user" : self.request.user.id})
        return context

    def get_template_names(self):
        return ["%s/%s_detail.html" % (self.get_object().polymorphic_ctype.app_label, self.get_object().polymorphic_ctype.model)]



class POIRatingView(CreateView):
    model = POI
    form_class = POIRatingForm
    http_method_names = ['post']

    def get_success_url(self):
        return reverse("poi-detail", kwargs={'slug' : self.get_object().slug})

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

@login_required
@staff_member_required
def convert_poi(request, pk, to_model):
    poi = POI.objects.get(id=pk)
    target_ct = ContentType.objects.get(model=to_model)
    target = target_ct.model_class().objects.create(poi_ptr_id=poi.id, name=poi.name, type=poi.type, geom=poi.geom)
    return redirect("admin:%s_%s_change" % (target_ct.app_label, target_ct.model), target.id)
