from rest_framework.serializers import ModelSerializer, SerializerMethodField
from poimap.serializers import POISerializer, PathSerializer
from .models import Line, Stop, Route, Service, Bus

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

class BusSerializer(ModelSerializer):
    class Meta:
        model = Bus
        fields = "__all__"

class LineSerializer(ModelSerializer):
    routes = RouteSerialized(many=True)
    buses = SerializerMethodField()

    def get_buses(self, obj):
        buses = []
        for service in Service.objects.filter(route__line=obj).order_by('route__line').distinct('route__line'):
            for bus in service.bus_set.all():
                if bus.license_plate:
                    buses.append(bus) 
        return BusSerializer(buses, many=True, read_only=True, context=self.context).data

    class Meta:
        model = Line
        fields = ("id", "name", "slug", "connection_info" ,"routes", 'buses')
