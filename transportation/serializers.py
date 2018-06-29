from rest_framework.serializers import ModelSerializer, SerializerMethodField
from poimap.serializers import POISerializer, PathSerializer
from .models import Line, Stop, Route

class StopSerializer(POISerializer):
    connection_count = SerializerMethodField()

    def get_connection_count(self, obj):
        return obj.route_set.all().count()

    class Meta(POISerializer.Meta):
        model = Stop
        fields = list(POISerializer.Meta.fields)
        fields.append("connection_count")

class RouteSerialized(ModelSerializer):
    path = PathSerializer()
    stops = SerializerMethodField()

    def get_stops(self, obj):
        return StopSerializer(obj.get_stops(), many=True, read_only=True, context=self.context).data

    class Meta:
        model = Route
        fields = ("id", "name", "slug", "direction", "path", "stops")

class LineSerializer(ModelSerializer):
    routes = RouteSerialized(many=True)

    class Meta:
        model = Line
        fields = ("id", "name", "slug", "connection_info" ,"routes")
