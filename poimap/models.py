# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gismodels
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_save

from cms.models.pluginmodel import CMSPlugin

from django_countries.fields import CountryField
from treebeard.mp_tree import MP_Node
from polymorphic.models import PolymorphicModel
from filer.fields.image import FilerImageField
from autoslug import AutoSlugField
from fontawesome.fields import IconField
from ckeditor.fields import RichTextField

from shapely.geometry import LineString, Point
from shapely.ops import split

import sys

class ImportationTrace(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')


class Area(models.Model):
    name = models.CharField(max_length=500)
    slug = AutoSlugField(populate_from="name", always_update=True)
    description = models.TextField(blank=True, null=True)
    geom = gismodels.GeometryField(dim=3)

    def __unicode__(self):
        return self.name


class Path(MP_Node):
    name = models.CharField(max_length=500)
    slug = AutoSlugField(populate_from="name", always_update=True)
    description = models.TextField(blank=True, null=True)
    geom = gismodels.LineStringField(dim=3)

    def __unicode__(self):
        return self.name


poi_child_models = getattr(settings, "POI_CHILD_MODELS", [])

class POIType(models.Model):
    label = models.CharField(max_length=30)
    slug = AutoSlugField(populate_from="label", always_update=True)
    icon = IconField()

    def get_typed_poi_count(self):
        return self.poi_set.count()


    def __unicode__(self):
        return "%s (%s)" % (self.label, self.get_typed_poi_count())

class POI(PolymorphicModel):
    name = models.CharField(max_length=500)
    related_path = models.ForeignKey(Path, null=True, blank=True)
    slug = AutoSlugField(populate_from="name", always_update=True)
    description = RichTextField(blank=True, null=True)
    type = models.ForeignKey(POIType)

    address = models.CharField(max_length=250, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    country = CountryField(default="FR")
    geom = gismodels.PointField(dim=3)

    starred = models.BooleanField(default=False)

    distance = models.PositiveIntegerField(default=0)

    @property
    def coords(self):
        return {
            "lat" : self.geom.coords[1],
            "lng" : self.geom.coords[0],
        }

    def __unicode__(self):
        return "%s - %s" % (self.name, self.type.label)

    class Meta:
        verbose_name = verbose_name_plural = "POI"
        ordering = ['distance', 'name']



@receiver(post_save, sender=POI)
def compute_distance(sender, instance, created, **kwargs):
    distance = 0
    if instance.related_path:
        path = instance.related_path
        poi = instance

        path.geom.transform(3035)
        poi.geom.transform(3035)

        line = LineString(path.geom.coords)
        point = Point(poi.geom.coords)
        min_dist = sys.maxint
        nearest_point = None
        for coord in line.coords:
            p = Point(coord)
            d = p.distance(point)
            if(d < min_dist):
                min_dist = d
                nearest_point = p
        subpath_length = split(line, nearest_point).geoms[0].length
        distance = line.distance(point)
        if subpath_length < line.length:
            distance += subpath_length
    sender.objects.filter(id=instance.id).update(distance=distance)

class POIMedia(models.Model):
    poi = models.ForeignKey(POI, related_name='medias')
    file = FilerImageField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["order"]
        verbose_name = "Photo"
        verbose_name_plural = "Gallerie"

class POIListing(CMSPlugin):
    type_display = models.ManyToManyField(POIType, verbose_name="Type de POI à afficher")

    def copy_relations(self, oldinstance):
        self.type_display = oldinstance.type_display.all()
