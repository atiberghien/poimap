# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from autoslug import AutoSlugField

from poimap.models import POI, poi_child_models

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
    stops = models.ManyToManyField("Stop", through="LineStop")

    def __unicode__(self):
        return "%s " % self.name


class LineStop(models.Model):
    line = models.ForeignKey(Line)
    stop = models.ForeignKey("Stop")
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order',)


class Stop(POI):
    slug = AutoSlugField(populate_from='name', always_update=True)

    def __unicode__(self):
        if self.description:
            return "%s (%s) " % (self.name, self.description)
        return self.name

poi_child_models.append(Stop)


class Route(models.Model):
    name = models.CharField(max_length=64)
    line = models.ForeignKey(Line, related_name="routes")
    slug = AutoSlugField(populate_from='name', always_update=True)
    periode = models.ManyToManyField(RunningDay)

    def __unicode__(self):
        return "%s / %s" % (self.line.name, self.name)

class TimeSlot(models.Model):
    hour = models.TimeField(null=True)
    stop = models.ForeignKey(Stop)
    route = models.ForeignKey(Route, related_name='timeslots')
    order = models.PositiveIntegerField(null=True)

    def __unicode__(self):
        return "%s - %s - %s " % (self.route, self.stop, self.hour)

    class Meta:
        ordering = ("hour", 'order')



@receiver(post_save,  sender=Route)
def autocreate_timeslot_for_route(sender, instance, created, **kwargs):
    if created:
        for stop in instance.line.stops.all():
            TimeSlot.objects.create(stop=stop, route=instance)


@receiver(post_save, sender=LineStop)
def update_route_timeslot(sender, instance, created, update_fields, **kwargs):
    for route in instance.line.routes.all():
        for linestop in LineStop.objects.filter(line=route.line):
            timeslot, nop = route.timeslots.get_or_create(stop=linestop.stop, route=route)
            timeslot.order = linestop.order
            timeslot.save()

@receiver(post_delete, sender=LineStop)
def delete_route_timeslot(sender, instance, **kwargs):
    for route in instance.line.routes.all():
        TimeSlot.objects.filter(stop=instance.stop, route=route).delete()
