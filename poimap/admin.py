#-*- coding: utf-8 -*-
from django import forms
from django.contrib.gis import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from leaflet.admin import LeafletGeoAdmin
from .models import POIType, POI, poi_child_models
from django.contrib.gis.gdal import OGRGeometry

class POIAdminForm(forms.ModelForm):
    gpx = forms.FileField(required=False)

    def clean_geom(self):
        """ Tricks to add default Z dimension into geometry """
        geom = self.cleaned_data["geom"]
        ogr = OGRGeometry(geom.wkt)
        ogr.coord_dim = 3
        return ogr.geos

    class Meta:
        model = POI
        fields = "__all__"

class POIAdmin(LeafletGeoAdmin):

    def __init__(self, *args, **kwargs):
        super(POIAdmin, self).__init__(*args, **kwargs)
        self.widget.supports_3d = True # for to be 3D friendly

    def convert_actions(self, obj):
        links = ""
        poi_ct = ContentType.objects.get(model='poi')
        if(obj.polymorphic_ctype != poi_ct):
            url = reverse("admin:%s_%s_change" % (obj.polymorphic_ctype.app_label, obj.polymorphic_ctype.model),
                           args=[obj.id])
            links = u'<a href="%s">Voir %s associés</a>' % (url, obj.polymorphic_ctype.model_class()._meta.verbose_name.title())
        else:
            #obj is just a POI
            for child_model in poi_child_models:
                links += '<a href="%s">Convertir en %s</a>' % (reverse("convert-poi", args=[obj.id, child_model._meta.model_name]),
                                                          child_model._meta.verbose_name.title())

        return links
    convert_actions.allow_tags = True
    convert_actions.short_description = ""

    list_display = ('id', 'name', 'type', 'convert_actions')
    list_editable = ('name', 'type')
    list_filter = ('type',)
    search_fields = ('name',)

    form = POIAdminForm

    fieldsets = (
        (None, {
            'fields': (('name', 'type'), 'description')
        }),
        (None, {
            'classes': ('address',),
            'fields': ('address',
                      ('zipcode', "city", 'country'),'gpx' )
        }),
        (None, {
            'classes': ('location',),
            'fields': ('geom',),
        }),
    )

    class Media:
        css = {
            "all": ('poimap/css/itinerary_form.css',),
        }
        js = (
            'poimap/js/poi_form.js',
            'bower_components/togeojson/togeojson.js',
        )

admin.site.register(POI, POIAdmin)
admin.site.register(POIType)
