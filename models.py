from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gismodels
from filer.fields.image import FilerImageField
from django_countries.fields import CountryField
from polymorphic.models import PolymorphicModel

DEFAULT_POI_ICON_CHOICES = (
    ("flag", "Drapeau"),
    ("cutlery", "Restaurant"),
    ("bed", "Hotel"),
    ("shopping-basket", "Magasin"),
    ("tint", "Point d'eau"),
    ("certificate", "Site touristique"),
)

icon_choices = getattr(settings, "POI_ICON_CHOICES", DEFAULT_POI_ICON_CHOICES)

class POIType(models.Model):  # POI = Point Of Interest
    label = models.CharField(max_length=30) # hotel gite chambre_hote camping autres
    icon = models.CharField(max_length=30, choices=icon_choices, default="flag")

    def __unicode__(self):
        return self.label


class POI(PolymorphicModel):
    name = models.CharField(max_length=500)         # nom du point de depart - Il pourrait aussi etre un hebergement
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(POIType)

    @property
    def address(self):
        return self.poiaddress_set.first()


class POIAddress(gismodels.Model):
    address = models.CharField(max_length=250, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    country = CountryField()
    poi = models.ForeignKey(POI)
    geom = gismodels.PointField()

# Create your models here.
class Base(models.Model):
    name = models.CharField(max_length=50)         # nom du point de depart - Il pourrait aussi etre un hebergement
    geo_coordinates = gismodels.PointField(null=True, blank=True)      # coordonnees du point de depart
    description = models.TextField(blank=True)
    media = FilerImageField(null=True, blank=True,)

    def __unicode__(self):
        return self.name
