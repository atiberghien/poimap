# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool
from .cms_models import POIListing, POIFilters, CustomItineraryFormPlugin, POI_LISTING_TEMPLATES
from .forms import CustomItineraryForm

from django.conf import settings
from shapely.geometry import box
from shapely.affinity import scale
from django.contrib.gis.geos import Polygon
from .models import Path, Area, POI

@plugin_pool.register_plugin
class POIListingPlugin(CMSPluginBase):
    model = POIListing
    name = _("POI List Plugin")
    render_template = POI_LISTING_TEMPLATES[0][0]
    cache = False

    def render(self, context, instance, placeholder):
        context = super(POIListingPlugin, self).render(context, instance, placeholder)
        request = context['request']
        if request.method == 'POST':
            #FIXME : must be in plugin setting
            path = Path.objects.first()
            form = CustomItineraryForm(request.POST)
            form.is_valid()
            data = form.cleaned_data
            start_point = data["start_point"]
            end_point = data["end_point"]
            bbox = box(start_point.coords["lng"], start_point.coords["lat"], end_point.coords["lng"], end_point.coords["lat"])
            bbox = scale(bbox, xfact=1.1, yfact=1.1)
            bbox = Polygon(list(bbox.exterior.coords))
            custom_path = path.geom.intersection(bbox)
            custom_path.transform(3035)
            length = custom_path.length / 1000
            custom_path.transform(4326)

            # step = data["step"]*1000
            # step_cpt = 1
            # margin = 5000
            # qs = POI.objects.filter(geom__within=bbox)
            # # for poi in qs:
            # #     print step_cpt*step-margin, poi.distance ,step_cpt*step+margin
            # #     if poi.distance >= step_cpt*step-margin and poi.distance <= step_cpt*step+margin:
            # #         print "youpi"
            # #     step_cpt += 1
            context.update({
                "start_point" : start_point,
                "end_point" : end_point,
                "step" : data["step"]*1000,
                "margin" : 5000,
                "path_slug" : path.slug,
                "poi_list" : POI.objects.filter(geom__within=bbox),
                "total_length" : length,
            })

        context["poi_type_slugs"] = instance.type_display.all().values_list('slug', flat=True)
        self.render_template = instance.template
        return context

@plugin_pool.register_plugin
class POIFiltersPlugin(CMSPluginBase):
    model = POIFilters
    name = _("POI Filters Plugin")
    render_template = "poimap/partial/poi_filters.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = CMSPluginBase.render(self, context, instance, placeholder)
        print(context["instance"].type_filters.all())
        return context


@plugin_pool.register_plugin
class ElevationPlugin(CMSPluginBase):
    model = CMSPlugin
    render_template = "poimap/partial/path_elevation_chart.html"
    cache = False


@plugin_pool.register_plugin
class CustomItineraryFormPlugin(CMSPluginBase):
    model = CustomItineraryFormPlugin
    render_template = "poimap/partial/custom_itinerary_form.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super(CustomItineraryFormPlugin, self).render(context, instance, placeholder)
        context.update({
            'form' : CustomItineraryForm()
        })
        return context
