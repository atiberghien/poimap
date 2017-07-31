from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import POI, POIType, Path, Area


class AreaSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Area
        geo_field = "geom"
        fields = ('slug', 'name', 'description')


class PathSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Path
        geo_field = "geom"
        fields = ('id', 'slug', 'name', 'description', 'is_root')


class POITypeSerializer(ModelSerializer):
    class Meta:
        model = POIType
        fields = ('label', 'slug', 'icon')


class POISerializer(GeoFeatureModelSerializer):
    type = POITypeSerializer()

    class Meta:
        model = POI
        geo_field = "geom"
        fields = ('id', 'name', 'slug', 'description', 'type', 'coords')

class TypedPOISerializer(ModelSerializer):

    poi_set = POISerializer(many=True, read_only=True)

    class Meta:
        model = POIType
        fields = ('label', 'slug', 'icon', 'poi_set')
