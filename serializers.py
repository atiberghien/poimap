from rest_framework.serializers import ModelSerializer, ListField, RelatedField
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from .models import POI, POIType

class POITypeSerializer(ModelSerializer):
    class Meta:
        model = POIType
        fields = ('label', 'icon')


class POISerializer(GeoFeatureModelSerializer):
    geom = GeometrySerializerMethodField()
    type = POITypeSerializer()

    def get_geom(self, obj):
        return obj.poiaddress_set.first().geom

    class Meta:
        model = POI
        geo_field = "geom"
        fields = ('id', 'name', 'description', 'type')

class TypedPOISerializer(ModelSerializer):

    poi_set = POISerializer(many=True, read_only=True)

    class Meta:
        model = POIType
        fields = ('label', 'icon', 'poi_set')
