# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gismodels
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.dispatch import receiver
from django.db.models.signals import post_save
from cms.models import CMSPlugin, Page
from django.db.models import Avg
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

    extra_data = JSONField(default=dict({}), blank=True)

    @property
    def coords(self):
        return {
            "lat" : self.geom.coords[1],
            "lng" : self.geom.coords[0],
        }

    @property
    def rating_score(self):
        return self.ratings.all().aggregate(Avg('score'))['score__avg'] or 0.0

    @property
    def vote_count(self):
        return self.ratings.count()

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

class POIRating(models.Model):
    poi = models.ForeignKey(POI, related_name='ratings')
    user = models.ForeignKey(User, null=True, blank=True)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "POI"
        ordering = ['-created_at',]

class POIMedia(models.Model):
    poi = models.ForeignKey(POI, related_name='medias')
    file = FilerImageField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["order"]
        verbose_name = "Photo"
        verbose_name_plural = "Gallerie"

POI_LISTING_TEMPLATES = (
  ('poimap/partial/poi_map_listing.html', 'Map'),
  ('poimap/partial/poi_listing.html', 'List'),
  ('poimap/partial/itinerary.html', 'Itinerary'),
)

class POIListing(CMSPlugin):
    area_display = models.ForeignKey(Area, null=True, blank=True, verbose_name="Zone à afficher")
    path_display = models.ForeignKey(Path, null=True, blank=True, verbose_name="Chemin à afficher")
    type_display = models.ManyToManyField(POIType, verbose_name="Type de POI à afficher")
    template = models.CharField('Template', max_length=255, choices=POI_LISTING_TEMPLATES, default="poimap/partial/poi_map_listing.html")
    hide_control = models.BooleanField(default=True)

    def copy_relations(self, oldinstance):
        self.type_display = oldinstance.type_display.all()

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
