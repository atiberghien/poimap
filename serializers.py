from poimap.serializers import POISerializer

from .models import Stop


class StopSerializer(POISerializer):
    class Meta(POISerializer.Meta):
        model = Stop
