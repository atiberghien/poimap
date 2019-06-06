# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.db.models import Avg, Count
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gismodels
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.dispatch import receiver
from django.utils.functional import lazy
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

    icon_file = FilerImageField(null=True, blank=True, on_delete=models.SET_NULL)
    color = models.CharField(max_length=30, null=True, blank=True)

    def get_typed_poi_count(self):
        return self.all_poi.count()

    def __unicode__(self):
        return u"%s (%s)" % (self.label, self.get_typed_poi_count())

def TYPE_SLUG_CHOICES():
    return [(t.slug, t.slug) for t in POIType.objects.all().order_by('slug')]

class SpecificPOITypeTemplate(models.Model):

    type_slug = models.CharField(max_length=500, choices=[])
    template_name = models.CharField(max_length=500)

    def __init__(self, *args, **kwargs):
        super(SpecificPOITypeTemplate, self).__init__(*args, **kwargs)
        self._meta.get_field('type_slug').choices = lazy(TYPE_SLUG_CHOICES, list)()

class POI(PolymorphicModel):
    name = models.CharField(max_length=500)
    related_path = models.ForeignKey(Path, null=True, blank=True)
    slug = AutoSlugField(populate_from="name", always_update=True)
    description = RichTextField(blank=True, null=True)
    type = models.ForeignKey(POIType, blank=True, null=True, on_delete=models.SET_NULL)
    types = models.ManyToManyField(POIType, related_name="all_poi")

    address = models.CharField(max_length=250, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    country = CountryField(default="FR")
    geom = gismodels.GeometryField(dim=3)
    altitude = models.FloatField(default=0.0)

    starred = models.BooleanField(default=False)

    distance = models.PositiveIntegerField(default=0, blank=True, null=True)

    extra_data = JSONField(default=list([dict({})]), blank=True, null=True)

    @property
    def coords(self):
        return {
            "lat" : self.geom.centroid.coords[1],
            "lng" : self.geom.centroid.coords[0],
        }

    @property
    def rating_score(self):
        return self.ratings.all().aggregate(Avg('score'))['score__avg'] or 0.0

    @property
    def vote_count(self):
        return self.ratings.count()

    def __unicode__(self):
        if self.type:
            return u"%s - %s" % (self.name, self.type.label)
        else:
            return u"%s" % self.name

    class Meta:
        verbose_name = verbose_name_plural = "POI"
        ordering = ['distance', 'name']


@receiver(post_save, sender=POI)
def fill_main_type(sender, instance, created, **kwargs):
    if not instance.type:
        POI.objects.filter(id=instance.id).update(type=instance.types.annotate(nb_poi=Count('all_poi')).order_by('nb_poi').first())
    elif not instance.types.count():
        instance.types.add(instance.type)

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
