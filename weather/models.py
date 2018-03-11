from __future__ import unicode_literals

from django.db import models
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import get_language
from django.contrib.postgres.fields import JSONField
from django.conf import settings

from poimap.models import POI
import pyowm
import json


class Weather(models.Model):
    poi = models.OneToOneField(POI, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    data = JSONField(null=True, blank=True)

    def fetch_data(self):
        if hasattr(settings, 'OWM_API_KEY'):
            print get_language()
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
        if not self.data:
            self.fetch_data()
        return json.loads(self.data)

    class Meta:
        ordering = ('poi__distance',)


class WeatherCMSPlugin(CMSPlugin):
    weathers = models.ManyToManyField(Weather)

    def copy_relations(self, oldinstance):
        self.weathers = oldinstance.weathers.all()
