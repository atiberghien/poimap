from rest_framework.serializers import ModelSerializer, SerializerMethodField
from poimap.serializers import POISerializer
from .models import Weather
import json


class WeatherSerializer(ModelSerializer):
    poi = POISerializer()
    weather = SerializerMethodField()

    def get_weather(self, obj):
        return obj.get_data()

    class Meta:
        model = Weather
        fields = ('poi', 'weather', 'updated_at')
