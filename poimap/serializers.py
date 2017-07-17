from rest_framework.serializers import ModelSerializer, ReadOnlyField, SerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import POI, POIType, Path, Area


class AreaSerializer(ModelSerializer):
    wkt = ReadOnlyField()
    class Meta:
        model = Area
        fields = ('slug', 'name', 'description', 'wkt')

class PathSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Path
        geo_field = "geom"
        fields = ('slug', 'name', 'description', 'is_root')

class POITypeSerializer(ModelSerializer):
    class Meta:
        model = POIType
        fields = ('label', 'icon')


class POISerializer(GeoFeatureModelSerializer):
    type = POITypeSerializer()

    class Meta:
        model = POI
        geo_field = "geom"
        fields = ('id', 'name', 'description', 'type', 'coords')

class TypedPOISerializer(ModelSerializer):

    poi_set = POISerializer(many=True, read_only=True)

    class Meta:
        model = POIType
        fields = ('label', 'icon', 'poi_set')
