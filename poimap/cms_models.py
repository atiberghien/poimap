# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin, Page
from .models import Area, Path, POIType, POI
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

POI_LISTING_TEMPLATES = (
    ('poimap/partial/poi_map_listing.html', 'Map'),
    ('poimap/partial/poi_listing.html', 'List'),
    ('poimap/partial/itinerary.html', 'Itinerary'),
)


class POIListing(CMSPlugin):
    area_display = models.ForeignKey(Area, null=True, blank=True, verbose_name=u"Zone à afficher", on_delete=models.SET_NULL)
    path_display = models.ForeignKey(Path, null=True, blank=True, verbose_name=u"Chemin à afficher", on_delete=models.SET_NULL)
    type_display = models.ManyToManyField(POIType, verbose_name=u"Type de POI à afficher")
    template = models.CharField('Template', max_length=255, choices=POI_LISTING_TEMPLATES, default="poimap/partial/poi_map_listing.html")
    hide_control = models.BooleanField(default=True)

    def copy_relations(self, oldinstance):
        self.type_display = oldinstance.type_display.all()



class POIFilters(CMSPlugin):
    type_filters = models.ManyToManyField(POIType, verbose_name=u"Type de POI à filter")

    def copy_relations(self, oldinstance):
        self.type_filters = oldinstance.type_filters.all()


class CustomItineraryFormPlugin(CMSPlugin):
    custom_link = models.CharField(
        verbose_name=_('Custom link'),
        blank=True,
        max_length=2040,
    )
    internal_link = models.ForeignKey(
        Page,
        verbose_name=_('Internal link'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    important_step_types = models.ManyToManyField(POIType, verbose_name=u"Types de étapes importantes")

    def copy_relations(self, oldinstance):
        self.important_step_types = oldinstance.important_step_types.all()

class POIDetailPluginModel(CMSPlugin):
    poi = models.ForeignKey(POI, on_delete=models.CASCADE)