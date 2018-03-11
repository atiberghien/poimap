
from rest_framework import generics
from .serializers import WeatherSerializer
from .models import Weather


class WeatherView(generics.RetrieveAPIView):
    queryset = Weather.objects.all()
    lookup_field = "poi__pk"
    serializer_class = WeatherSerializer
