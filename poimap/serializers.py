from django.template.loader import render_to_string
from rest_framework.serializers import ModelSerializer, SerializerMethodField, HyperlinkedIdentityField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import *

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
    icon_file_url = SerializerMethodField()
    icon = SerializerMethodField()

    def get_icon_file_url(self, obj):
        return obj.icon_file.url if obj.icon_file else ""
    
    def get_icon(self, obj):
        if obj.icon:
            return obj.icon.name
        return ""
    
    class Meta:
        model = POIType
        fields = ('label', 'slug', 'icon', 'icon_file_url', 'color')

class POIMediaSerializer(ModelSerializer):
    class Meta:
        model = POIMedia
        fields = "__all__"


class POISerializer(GeoFeatureModelSerializer):
    type = POITypeSerializer()
    marker_popup = SerializerMethodField()
    medias = SerializerMethodField()
    api_url = HyperlinkedIdentityField(view_name='poi-api-detail', read_only=True)
    url = HyperlinkedIdentityField(view_name='poi-detail', lookup_field="slug", read_only=True)
    rating_score = SerializerMethodField()
    vote_count = SerializerMethodField()
    extra_data = SerializerMethodField()

    def get_rating_score(self, obj):
        return obj.rating_score

    def get_vote_count(self, obj):
        return obj.vote_count

    def get_marker_popup(self, obj):
        return render_to_string("poimap/partial/poi_marker_popup.html", {"object" : obj})

    def get_medias(self, obj):
        return obj.medias.values_list('file__file', flat=True)

    def get_extra_data(self, obj):
        return obj.get_real_instance().get_extra_data()

    class Meta:
        model = POI
        geo_field = "geom"
        fields = ['id', 'name', 'slug', 'description', 'distance', 'type', 'coords', "city", "marker_popup", "medias", "url", "api_url", 'rating_score', 'vote_count', 'extra_data']

class TypedPOISerializer(ModelSerializer):

    poi_set = POISerializer(many=True, read_only=True)

    class Meta:
        model = POIType
        fields = ('label', 'slug', 'icon', 'poi_set')
