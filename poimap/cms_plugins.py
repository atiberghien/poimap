# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool
from .cms_models import POIListing, POIFilters, CustomItineraryFormPlugin, POI_LISTING_TEMPLATES
from .cms_models import POIDetailPluginModel, POISearchAutocompletePluginModel
from .forms import CustomItineraryForm

from django.conf import settings
from shapely.geometry import box
from shapely.affinity import scale
from django.contrib.gis.geos import Polygon
from .models import Path, Area, POI, POIType
from collections import OrderedDict
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
            important_step_type_ids = [int(id) for id in request.POST.get("important_step_type_ids").split(",")]
            
            bbox = box(start_point.coords["lng"], start_point.coords["lat"], end_point.coords["lng"], end_point.coords["lat"])
            bbox = scale(bbox, xfact=1.1, yfact=1.1)
            bbox = Polygon(list(bbox.exterior.coords))

            tolerance = 5.0 #km

            related_poi = POI.objects.filter(starred=False, geom__within=bbox)

            min_distance = related_poi.first().distance / 1000
            max_distance = related_poi.last().distance / 1000

            steps = [(0.0, tolerance)]
            current_step = data["step"]
            while current_step + min_distance < max_distance:
                steps.append((current_step - tolerance if current_step - tolerance > 0 else 0, 
                              current_step + tolerance if current_step + tolerance < max_distance else max_distance))
                current_step += data["step"]
            steps.append((max_distance - tolerance, max_distance + tolerance))


            for poi in related_poi:
                poi.relative_distance_km = (poi.distance - min_distance) / 1000.0
                poi.is_important = False

                if poi.type.id in important_step_type_ids:
                    poi.is_important = True
                    poi.is_step = False

                    cpt = 0
                    while cpt < len(steps) and not poi.is_step:
                        low_step, high_step = steps[cpt]
                        poi.is_step = low_step <= poi.relative_distance_km <= high_step
                        cpt+=1
            
            all_steps = [([],[])]
            nb_step = 1
            current_step = data["step"]
            for poi in related_poi:
                if poi.relative_distance_km > current_step:
                    all_steps.append(([],[]))
                    nb_step+=1
                    current_step =  nb_step * data["step"]
                if poi.is_important:
                    all_steps[-1][0].append(poi)
                else:
                    all_steps[-1][1].append(poi)

            context.update({
                "start_point" : start_point,
                "end_point" : end_point,
                "step_km" : data["step"],
                "margin" : 5000,
                "path_slug" : path.slug,
                "poi_list" : related_poi,
                "all_steps" : all_steps,
                "total_length" : max_distance,
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
            'form' : CustomItineraryForm(),
            'important_step_type_ids' : ",".join([str(i) for i in instance.important_step_types.values_list('id', flat=True)])
        })
        return context

@plugin_pool.register_plugin
class POIDetailPlugin(CMSPluginBase):
    model = POIDetailPluginModel
    render_template = "poimap/partial/poi_detail_map.html"


@plugin_pool.register_plugin
class POISearchAutocompletePlugin(CMSPluginBase):
    model = POISearchAutocompletePluginModel
    render_template = "poimap/partial/poi_search_autocomplete.html"

    def render(self, context, instance, placeholder):
        context = super(POISearchAutocompletePlugin, self).render(context, instance, placeholder)
        context.update({
            "search_types" : ",".join([t for t in instance.search_types.values_list('slug', flat=True)])
        })
        return context