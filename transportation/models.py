# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.contrib.postgres.fields import JSONField
from django.dispatch import receiver
from autoslug import AutoSlugField
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
from filer.fields.folder import FilerFolderField
from ckeditor.fields import RichTextField
from dateutil import rrule
from dateutil.parser import parse
from dateutil.rrule import rrulestr

from poimap.models import POI, Path

class Line(models.Model):
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name', always_update=True)

    connection_info = RichTextField(null=True, blank=True)

    def get_bus(self):
        bus_list = []
        for route in self.routes.all():
            for service in route.services.all():
                bus_list.extend(list(service.bus_set.all()))
        return set(bus_list)
                    
    def __unicode__(self):
        return "%s " % self.name

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
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=64)
    slug = AutoSlugField(populate_from='name', always_update=True)
    route = models.ForeignKey(Route, related_name="services")
    frequency_label = models.CharField(max_length=10)
    recurrences = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    @property
    def rruleset(self):
        res = rrule.rruleset()
        rule_str = [r.strip("\n\r\t ").replace(" ", "") for r in self.recurrences.split("|")]
        for r in rule_str:
            if r:
                if "RRULE" in r:
                    rule = rrulestr(r)
                    res.rrule(rule)
                elif "EXRULE" in r:
                    rule = rrulestr(r)
                    res.exrule(rule)
                elif "EXDATE" in r:
                    d = r.split(":")[1]
                    res.exdate(parse(d))
                elif "RDATE" in r:
                    d = r.split(":")[1]
                    res.rdate(parse(d))
        return res

    def __unicode__(self):
        return "%s - %s - %s" % (self.route.line.name, self.route.name, self.name)

    class Meta:
        ordering = ('name',)

class TimeSlot(models.Model):
    hour = models.TimeField(null=True, blank=True)
    stop = models.ForeignKey(Stop)
    service = models.ForeignKey(Service, related_name='timeslots')
    order = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return "%s - %s - %s " % (self.service, self.stop, self.hour)

    class Meta:
        ordering = ('order',)


class Travel(models.Model):
    stop1 = models.ForeignKey(Stop, related_name="start_edges")
    stop2 = models.ForeignKey(Stop, related_name="end_edges")
    distance = models.PositiveIntegerField(default=0)
    price = models.FloatField(null=True, blank=True)
    routes = models.ManyToManyField(Route)


class Bus(models.Model):
    name = models.CharField(max_length=64)
    slug = AutoSlugField(populate_from='name', always_update=True)
    blueprint = FilerFileField(null=True, blank=True)
    nb_seats = models.PositiveIntegerField(default=0)
    services = models.ManyToManyField(Service)
    picture = FilerImageField(null=True, blank=True, related_name="+")
    cover = FilerImageField(null=True, blank=True, related_name="+")
    gallery = FilerFolderField(null=True, blank=True, related_name="+")
    index_eco = models.PositiveIntegerField(default=0)
    equipments = RichTextField(blank=True, null=True, config_name='only_bullet_point')



class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    terms = models.BooleanField()
    privacy = models.BooleanField()
    optin = models.BooleanField()


class Order(models.Model):
    num = models.CharField(max_length=500, unique=True)
    customer = models.ForeignKey(Customer)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def total_amount(self):
        return sum(list(self.ticket_set.values_list("price", flat=True)))
    total_amount.description = "Total Amount"



class Ticket(models.Model):
    num = models.CharField(max_length=500, unique=True)
    order = models.ForeignKey(Order)
    traveller_first_name = models.CharField(max_length=255)
    traveller_last_name = models.CharField(max_length=255)
    date = models.DateField()
    departure_stop = models.ForeignKey(Stop, related_name="ticket_arrival_stops")
    arrival_stop = models.ForeignKey(Stop, related_name="ticket_departure_stops")
    departure_hour = models.TimeField()
    arrival_hour = models.TimeField()
    price = models.FloatField()

    is_validated = models.BooleanField(default=False)

class Connection(models.Model):
    ticket = models.ForeignKey(Ticket)
    service = models.ForeignKey(Service)
    from_stop = models.ForeignKey(Stop, related_name="+")
    to_stop = models.ForeignKey(Stop, related_name="+")
    seat = models.IntegerField(null=True, blank=True)



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
