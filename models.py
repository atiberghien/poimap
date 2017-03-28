from django.db import models
from filer.models import File
from django.contrib.gis.db import models as gismodels
from filer.fields.image import FilerImageField


# Create your models here.
class Base(models.Model):
    name = models.CharField(max_length=50)         # nom du point de depart - Il pourrait aussi etre un hebergement
    geo_coordinates = gismodels.PointField(null=True, blank=True)      # coordonnees du point de depart
    description = models.TextField(blank=True)
    media = FilerImageField(null=True, blank=True,)

    def __unicode__(self):
        return self.name
