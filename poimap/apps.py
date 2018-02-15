from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_save

class PoiMapConfig(AppConfig):
    name = 'poimap'

    def ready(self):
        from .models import POI, compute_distance
        for subclass in POI.__subclasses__():
            post_save.connect(compute_distance, subclass)
