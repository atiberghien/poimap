from rest_framework import generics
from .serializers import StopSerializer
from .models import Stop

class StopListView(generics.ListAPIView):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
