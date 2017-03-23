from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.db.models import PointField
from filer.models import File
from filer.fields.image import FilerImageField


# Create your models here.
class Base(models.Model):
    name = models.CharField(max_length=50)         # nom du point de depart - Il pourrait aussi etre un hebergement
    geo_coordinates = models.PointField(null=True, blank=True)      # coordonnees du point de depart
    description = models.TextField(blank=True)
    media = FilerImageField(null=True, blank=True,)

    def __unicode__(self):
        return self.name
