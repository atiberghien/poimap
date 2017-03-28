from django.db import models
from django.contrib.gis.db import models as gismodels
from filer.fields.image import FilerImageField
from django_countries.fields import CountryField


class POIAddress(gismodels.Model):
    address = models.CharField(max_length=250)
    zipcode = models.CharField(max_length=10)
    city = models.CharField(max_length=300)
    country = CountryField()
    geom = gismodels.PointField()

class POIType(models.Model):  # POI = Point Of Interest
    label = models.CharField(max_length=30)         # hotel gite chambre_hote camping autres

    def __unicode__(self):
        return self.label


# Create your models here.
class Base(models.Model):
    name = models.CharField(max_length=50)         # nom du point de depart - Il pourrait aussi etre un hebergement
    geo_coordinates = gismodels.PointField(null=True, blank=True)      # coordonnees du point de depart
    description = models.TextField(blank=True)
    media = FilerImageField(null=True, blank=True,)

    def __unicode__(self):
        return self.name
