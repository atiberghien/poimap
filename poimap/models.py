from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gismodels
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django_countries.fields import CountryField
from treebeard.mp_tree import MP_Node
from polymorphic.models import PolymorphicModel

from autoslug import AutoSlugField
from fontawesome.fields import IconField
from ckeditor.fields import RichTextField


class ImportationTrace(models.Model):
    original_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField()
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
        return self.label

class POI(PolymorphicModel):
    name = models.CharField(max_length=500)
    slug = AutoSlugField(populate_from="name", always_update=True)
    description = RichTextField(blank=True, null=True)
    type = models.ForeignKey(POIType)

    address = models.CharField(max_length=250, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    country = CountryField(default="FR")
    geom = gismodels.PointField(dim=3)

    starred = models.BooleanField(default=False)

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
