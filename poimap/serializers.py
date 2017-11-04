from django.template.loader import render_to_string
from rest_framework.serializers import ModelSerializer, SerializerMethodField
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
    marker_popup = SerializerMethodField()

    def get_marker_popup(self, obj):
        return render_to_string("poimap/partial/poi_marker_popup.html", {"object" : obj})

    class Meta:
        model = POI
        geo_field = "geom"
        fields = ('id', 'name', 'slug', 'description', 'type', 'coords', "marker_popup")

class TypedPOISerializer(ModelSerializer):

    poi_set = POISerializer(many=True, read_only=True)

    class Meta:
        model = POIType
        fields = ('label', 'slug', 'icon', 'poi_set')
