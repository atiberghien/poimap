from __future__ import unicode_literals

from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.db.models import PointField
from filer.models import File
from filer.fields.image import FilerImageField

# Create your models here.
class HostingType(models.Model):
    label = models.CharField(max_length=30)         # hotel gite chambre_hote camping autres

    def __unicode__(self):
        return self.label

class PaymentType(models.Model):
    label = models.CharField(max_length=30)         # hotel gite chambre_hote camping autres

    def __unicode__(self):
        return self.label


class Hostings(models.Model):
    RESPONSES_CHOICES = (
    ('1', 'Oui'),
    ('2', 'Non'),
    ('3', 'A la demande'),
    )
    hosting_type = models.ForeignKey(HostingType)
    accepted_payments = models.ManyToManyField(PaymentType)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    zipcode = models.CharField(max_length=50)
    city = models.CharField(max_length=300)
    phone = models.CharField(max_length=15, blank=True)
    fax = models.CharField(max_length=15, blank=True)
    email = models.CharField(max_length=150, blank=True)
    web = models.CharField(max_length=150, blank=True)
    geo_coordinates = models.PointField(null=True, blank=True)
    description = models.TextField(blank=True)
    media = FilerImageField(null=True, blank=True,)
    food = models.BooleanField(default=False) # restauration
    picnic = models.CharField(
        max_length=1,
        choices=RESPONSES_CHOICES,
        default=1,
        ) # pique nique du lendemain
    picnic_price = models.FloatField(null=True, blank=True)
    car_parking = models.BooleanField(default=False) # parking voiture
    cycle_garage = models.BooleanField(default=False) # garage velo
    stable = models.BooleanField(default=False) # ecurie anes chevaux
    disabled_access = models.BooleanField(default=False) # acces handicape
    wifi = models.BooleanField(default=False)
    pets = models.BooleanField(default=False) # animaux de compagnie
    booking_phone_only = models.BooleanField(default=False) # reservation par tel uniquement
    food_shop = models.BooleanField(default=False)
    washing_machine = models.BooleanField(default=False) # lave linge
    tumble_drier = models.BooleanField(default=False) # seche linge
    sheet_renting = models.BooleanField(default=False) # location de draps
    pool = models.BooleanField(default=False) # piscine
    spa = models.BooleanField(default=False)
    jacuzzi = models.BooleanField(default=False)
    bivouac = models.BooleanField(default=False)
    min_price = models.FloatField(null=True, blank=True)
    max_price = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return '%s, %s, %s' % (self.name, self.zipcode, self.city)


class OpeningDate(models.Model):
    hosting = models.ForeignKey(Hostings)
    start_date = models.DateField()
    end_date = models.DateField()
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    public_holiday = models.BooleanField(default=False)

    def __unicode__(self):
        return self.hosting


class Contact(models.Model):
    hosting = models.ForeignKey(Hostings)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mobile_phone = models.CharField(max_length=10, blank=True)
    email = models.EmailField(max_length = 150, blank=True)

    def __unicode__(self):
        return '%s, %s' % (self.first_name, self.last_name)


class SleepingType(models.Model):       # type de couchage
    label = models.CharField(max_length=30)         # chambre suite dortoir mobilhome ...

    def __unicode__(self):
        return self.label


class Sleeping(models.Model):
    hosting = models.ForeignKey(Hostings)
    sleeping_type = models.ForeignKey(SleepingType)
    name = models.CharField(max_length=30)      # nom ou numero du couchage
    places = models.FloatField(null=True, blank=True)
    comments = models.TextField()       # lits kitchnette micro ondes bouilloire cafetiere ...
    wc_where = models.BooleanField(default=True)     # true = dans la chambre
    SANITATION_CHOICES = (
    ('1', 'Douche'),
    ('2', 'Baignoire'),
    ('3', 'Douche + Baignoire'),
    )
    sanitation = models.CharField(
        max_length=1,
        choices=SANITATION_CHOICES,
        default=1,
    )
    sanitation_where = models.BooleanField(default=True)     # true = dans la chambre
    RESPONSES_CHOICES = (
    ('1', 'Oui'),
    ('2', 'Non'),
    ('3', 'A la demande'),
    )
    breakfast = models.CharField(
        max_length=1,
        choices=RESPONSES_CHOICES,
        default=1,
    )
    breakfast_price = models.FloatField(null=True, blank=True)
    half_board = models.CharField(
        max_length=1,
        choices=RESPONSES_CHOICES,
        default=1,
    )
    half_board_price = models.FloatField(null=True, blank=True)
    price_1person = models.FloatField(null=True, blank=True)
    price_Xperson = models.FloatField(null=True, blank=True)
