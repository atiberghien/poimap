# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from autoslug import AutoSlugField
from dateutil import rrule
from dateutil.parser import parse
from dateutil.rrule import rrulestr

from poimap.models import POI, Path

class Fare(models.Model):
    FARE_TYPE_CHOICES = (
        ('A', 'Abonnement'),
        ('T', 'Ticket'),
    )
    type = models.CharField(max_length=1, choices=FARE_TYPE_CHOICES)
    price = models.FloatField()
    valid_for = models.TextField()
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "%s, %s" % (self.type, self.price)

class RunningDay(models.Model):
    PERIOD_CHOICES = (
        ('1', 'Lundi'),
        ('2', 'Mardi'),
        ('3', 'Mercredi'),
        ('4', 'Jeudi'),
        ('5', 'Vendredi'),
        ('6', 'Samedi'),
        ('7', 'Dimanche ou jours feries'),
        ('8', 'Vacances Scolaire'),
        ('9', 'Hors Vacances'),
    )
    period = models.CharField(max_length=1, choices=PERIOD_CHOICES, unique=True)

    def __unicode__(self):
        return "%s " % (self.get_period_display())

class Line(models.Model):
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name', always_update=True)

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


class GraphEdge(models.Model):
    stop1 = models.ForeignKey(Stop, related_name="start_edges")
    stop2 = models.ForeignKey(Stop, related_name="end_edges")
    distance = models.PositiveIntegerField(default=0)
    routes = models.ManyToManyField(Route)

@receiver(post_save,  sender=Service)
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
