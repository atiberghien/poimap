# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.shortcuts import reverse
from django.dispatch import receiver
from autoslug import AutoSlugField
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
from filer.fields.folder import FilerFolderField
from ckeditor.fields import RichTextField
from dateutil.parser import parse
from dateutil import rrule
from dateutil.rrule import rrulestr
from django.contrib.postgres.fields import ArrayField
from dateutil.tz import tzutc

from poimap.models import POI, Path
from facilities.models import WorkingPeriod, DayOff
from datetime import datetime
from dateutil.rrule import rrule, rruleset, WEEKLY, MO, TU, WE, TH, FR, SA, SU

class CustomPermissions(models.Model):

    class Meta:

        managed = False 

        permissions = ( 
            ('access_driver_infos', 'Access to driver infos'),  
            ('access_sms_announcement', 'Access SMS announcement form'), 
        )

class Line(models.Model):
    name = models.CharField(max_length=150, verbose_name="nom")
    number = models.CharField(max_length=10, default="", verbose_name="numéro")
    
    slug = AutoSlugField(populate_from='name', always_update=True)

    connection_info = RichTextField(null=True, blank=True, verbose_name="correspondance")

    prices = FilerFileField(null=True, blank=True, verbose_name="grilles tarifaires")

    carbon_footprint = models.CharField(max_length=40, default="0", verbose_name="émission carbone")

    def get_bus(self):
        bus_list = []
        for route in self.routes.all():
            for service in route.services.all():
                bus_list.extend(list(service.bus_set.all()))
        return set(bus_list)
                    
    def __unicode__(self):
        return "%s " % self.name
    
    class Meta:
        verbose_name = "ligne"

class Route(models.Model):
    DIRECTION_CHOICES = (
        ('1', 'Aller'),
        ('2', 'Retour')
    )
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name', always_update=True)
    line = models.ForeignKey(Line, related_name="routes")
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES, default="1")
    path = models.ForeignKey(Path, null=True, blank=True)
    stops = models.ManyToManyField("Stop", through="RouteStop")

    def __unicode__(self):
        return "%s - %s (%s)" % (self.line.name, self.name, self.get_direction_display())

    def get_stops(self):
        return self.stops.order_by("stop")

    class Meta:
        unique_together = ("line", "direction")
        ordering = ('id', 'direction')

class RouteStop(models.Model):
    route = models.ForeignKey(Route)
    stop = models.ForeignKey("Stop", related_name='stop')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order',)


class Stop(POI):

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ('name',)


class Service(WorkingPeriod):
    name = models.CharField(max_length=64)
    slug = AutoSlugField(populate_from='name', always_update=True, unique=True)
    route = models.ForeignKey(Route, related_name="services")

    frequency_label = models.CharField(max_length=10)
    recurrences = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(verbose_name="Active ?", default=True)
    is_temporary = models.BooleanField(verbose_name="Temp ?", default=False)

    @property
    def rruleset(self):
        rset =  WorkingPeriod.rruleset(self)
        for extra_period in self.extra_periods.all():
            for d in extra_period.rruleset():
                if extra_period.include:
                    rset.rdate(d)
                else:
                    rset.exdate(d)
        return rset
    
    # @property
    # def frequency(self):
    #     return "".join([
    #         'L' if self.monday else '-',
    #         'M' if self.tuesday else '-',   
    #         'M' if self.wednesday else '-',   
    #         'J' if self.thursday else '-',   
    #         'V' if self.friday else '-',   
    #         'S' if self.saturday else '-',   
    #         'D' if self.sunday else '-',   
    #         'F' if self.days_off else '-'  
    #     ])

    def __unicode__(self):
        return "%s - %s - %s" % (self.name, self.route.line.name, self.route.name)

    class Meta:
        ordering = ('name',)

class ServiceWorkingPeriod(WorkingPeriod):
    service = models.ForeignKey(Service, related_name="extra_periods")

class TimeSlot(models.Model):
    hour = models.TimeField(null=True, blank=True)
    stop = models.ForeignKey(Stop)
    service = models.ForeignKey(Service, related_name='timeslots')
    is_next_day = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        # return "%s - %s - %s " % (self.service, self.stop, self.hour)
        return "%s" % self.stop


    class Meta:
        ordering = ('order',)


class Travel(models.Model):
    stop1 = models.ForeignKey(Stop, related_name="start_edges")
    stop2 = models.ForeignKey(Stop, related_name="end_edges")
    distance = models.PositiveIntegerField(default=0)
    price = models.FloatField(null=True, blank=True)
    routes = models.ManyToManyField(Route)

    class Meta:
        ordering = ('stop1__name', 'distance')

class Bus(models.Model):
    name = models.CharField(max_length=64)
    slug = AutoSlugField(populate_from='name', always_update=True, unique=True)
    license_plate = models.CharField(max_length=20, null=True, blank=True)
    blueprint = FilerFileField(null=True, blank=True, on_delete=models.CASCADE)
    nb_seats = models.PositiveIntegerField(default=0)
    services = models.ManyToManyField(Service)
    picture = FilerImageField(null=True, blank=True, related_name="+", on_delete=models.CASCADE)
    cover = FilerImageField(null=True, blank=True, related_name="+")
    gallery = FilerFolderField(null=True, blank=True, related_name="+", on_delete=models.CASCADE)
    index_eco = models.PositiveIntegerField(default=0)
    description = RichTextField(blank=True, null=True)
    equipments = RichTextField(blank=True, null=True, config_name='only_bullet_point')
    confort = RichTextField(blank=True, null=True, config_name='only_bullet_point')
    security = RichTextField(blank=True, null=True, config_name='only_bullet_point')

    def get_absolute_url(self):
        return reverse("transportation-fleet-vehicule", args=[self.slug])


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)

    sms_notif = models.BooleanField(default=False)
    terms = models.BooleanField()
    privacy = models.BooleanField()
    optin = models.BooleanField()

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        ordering = ("last_name", "first_name", "email")
        verbose_name = "client"


class Order(models.Model):
    num = models.CharField(max_length=500, unique=True)
    customer = models.ForeignKey(Customer)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    
    def total_amount(self):
        return sum(list(self.ticket_set.values_list("price", flat=True)))
    total_amount.description = "Total Amount"


class Ticket(models.Model):
    num = models.CharField(max_length=500, unique=True)
    order = models.ForeignKey(Order)
    traveller_first_name = models.CharField(max_length=255)
    traveller_last_name = models.CharField(max_length=255)
    date = models.DateField()
    departure_stop = models.ForeignKey(Stop, related_name="ticket_departure_stops")
    arrival_stop = models.ForeignKey(Stop, related_name="ticket_arrival_stops")
    departure_hour = models.TimeField()
    arrival_hour = models.TimeField()
    price = models.FloatField()

    is_validated = models.BooleanField(default=False)

    class Meta:
        ordering = ('date', 'departure_hour')

class Connection(models.Model):
    ticket = models.ForeignKey(Ticket)
    service = models.ForeignKey(Service)
    from_stop = models.ForeignKey(Stop, related_name="+")
    to_stop = models.ForeignKey(Stop, related_name="+")
    seat = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('id',)


class PartnerSearch(models.Model):
    departure_stop = models.ForeignKey(Stop, related_name="+")
    arrival_stop = models.ForeignKey(Stop, related_name="+")
    travel_date = models.DateTimeField()
    partner = models.CharField(max_length=200)
    search_date = models.DateTimeField(auto_now_add=True)
    info = models.CharField(max_length=500, blank=True)

    def get_absolute_url(self):
        return reverse("deeplink-partner", args=[self.departure_stop.slug, self.arrival_stop.slug])

class SMSNotification(models.Model):
    phone = models.CharField(max_length=255, unique=True)

    future_sms = ArrayField(models.CharField(max_length=200), null=True, blank=True)

class SMSAnnouncement(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="créé le")
    service = models.ForeignKey(Service)
    departure_datetime = models.DateTimeField(verbose_name="date/heure de départ")
    notification_datetime = models.DateTimeField(verbose_name="date/heure de la notification")
    message = models.TextField()

    class Meta:
        verbose_name = "annonce SMS"
        verbose_name_plural = "annonces SMS"

@receiver(post_save, sender=Service)
def autocreate_timeslot_for_service(sender, instance, created, **kwargs):
    if created:
        i = 0
        for stop in instance.route.get_stops():
            TimeSlot.objects.create(stop=stop, service=instance, order=i)
            i += 1

@receiver(post_save, sender=RouteStop)
def update_service_timeslot(sender, instance, created, update_fields, **kwargs):
    for service in instance.route.services.all():
        for routestop in RouteStop.objects.filter(route=service.route):
            timeslot, nop = service.timeslots.get_or_create(stop=routestop.stop, service=service)
            timeslot.order = routestop.order
            timeslot.save()

@receiver(post_delete, sender=RouteStop)
def delete_service_timeslot(sender, instance, **kwargs):
    for service in instance.route.services.all():
        TimeSlot.objects.filter(stop=instance.stop, service=service).delete()


@receiver(post_save, sender=Line)
@receiver(post_save, sender=Route)
@receiver(post_save, sender=Stop)
@receiver(post_save, sender=Path)
@receiver(post_save, sender=Service)
@receiver(post_save, sender=TimeSlot)
def flush_cache(sender, instance, created, **kwargs):
    try:
        from django_redis import get_redis_connection
        get_redis_connection("default").flushall()
    except:
        pass

