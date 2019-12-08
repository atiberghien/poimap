# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

class DayOff(models.Model):
    date = models.DateField(unique=True)
    desc = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        ordering = ('date',)

class WorkingDays(models.Model):
    monday = models.BooleanField(verbose_name=_('Lundi'), default=False)
    tuesday = models.BooleanField(verbose_name=_('Mardi'), default=False)
    wednesday = models.BooleanField(verbose_name=_('Mercredi'), default=False)
    thursday = models.BooleanField(verbose_name=_('Jeudi'), default=False)
    friday = models.BooleanField(verbose_name=_('Vendredi'), default=False)
    saturday = models.BooleanField(verbose_name=_('Samedi'), default=False)
    sunday = models.BooleanField(verbose_name=_('Dimanche'), default=False)
    days_off = models.BooleanField(verbose_name=_('Fériés'), default=False)

    class Meta:
        abstract = True

class WorkingPeriod(WorkingDays):
    from_date = models.DateField()
    to_date = models.DateField()

    class Meta:
        abstract = True

