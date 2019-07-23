from __future__ import unicode_literals

from django.db import models
from cms.models.pluginmodel import CMSPlugin
from django.contrib.postgres.fields import JSONField
from django.conf import settings

from poimap.models import POI
import pyowm
import json
from datetime import datetime, timedelta

class Weather(models.Model):
    poi = models.OneToOneField(POI, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    data = JSONField(default=list, null=True, blank=True)

    def fetch_data(self):
        if hasattr(settings, 'OWM_API_KEY'):
            owm = pyowm.OWM(settings.OWM_API_KEY, language='fr')
            coords = self.poi.geom.coords
            observation = owm.weather_at_coords(coords[1], coords[0])
            w = observation.get_weather()
            owm_data = json.loads(w.to_JSON())
            del owm_data["temperature"]
            owm_data["temperature_c"] = w.get_temperature(unit="celsius")
            owm_data["temperature_f"] = w.get_temperature(unit="fahrenheit")
            owm_data["temperature_k"] = w.get_temperature(unit="kelvin")
            self.data = json.dumps(owm_data)
            self.save()

    def get_data(self):
        now = datetime.now().replace(tzinfo=None)
        td = now - self.updated_at.replace(tzinfo=None)
        d = timedelta(hours=2)
        if not self.data or td > d:
            self.fetch_data()
        return json.loads(self.data)

    def __str__(self):
        return self.poi.name.encode("utf-8")

    class Meta:
        ordering = ('poi__distance',)


class WeatherCMSPlugin(CMSPlugin):
    weathers = models.ManyToManyField(Weather)

    def copy_relations(self, oldinstance):
        self.weathers = oldinstance.weathers.all()
