# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from dateutil.rrule import rrule, rruleset, WEEKLY, MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import tzutc

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
    include = models.BooleanField(verbose_name=_('Inclure/Exclure ?'), default=True)
    from_date = models.DateField()
    to_date = models.DateField()

    def rruleset(self):
        weekdays = []
        if self.monday:
            weekdays.append(MO)
        if self.tuesday: 
            weekdays.append(TU)
        if self.wednesday: 
            weekdays.append(WE)
        if self.thursday: 
            weekdays.append(TH)
        if self.friday: 
            weekdays.append(FR)
        if self.saturday: 
            weekdays.append(SA) 
        if self.sunday:    
            weekdays.append(SU) 

        rset = rruleset()
        dfrom = datetime.combine(self.from_date, datetime.min.time()).replace(tzinfo=tzutc())
        dto = datetime.combine(self.to_date, datetime.max.time()).replace(tzinfo=tzutc())
        
        rset.rrule(rrule(WEEKLY, dtstart=dfrom, until=dto, byweekday=weekdays))
        
        today = datetime.today()
        for d in DayOff.objects.filter(date__year=today.year):
            date = datetime.combine(d.date, datetime.min.time()).replace(tzinfo=tzutc())
            
            if self.days_off:
                rset.rdate(date)
            else:
                rset.exdate(date)
        
        return rset

    class Meta:
        abstract = True

