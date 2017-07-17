#-*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.gis import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.contrib.gis.gdal import OGRGeometry

from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from treebeard.admin import TreeAdmin
from treebeard.forms import MoveNodeForm, movenodeform_factory

from .models import POIType, POI, poi_child_models, Area, Path

class AreaAdmin(LeafletGeoAdmin):
    list_display = ('name',)

    class Meta:
        model = Area
        fields = '__all__'


class PathAdminForm(MoveNodeForm):

    def clean_geom(self):
        """ Tricks to add default Z dimension into geometry """
        geom = self.cleaned_data["geom"]
        ogr = OGRGeometry(geom.wkt)
        ogr.coord_dim = 3
        return ogr.geos

    class Meta:
        model = Path
        fields = "__all__"

class PathAdmin(LeafletGeoAdminMixin, TreeAdmin):
    form = movenodeform_factory(Path, form=PathAdminForm)
    list_display = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name',
            ('_position', '_ref_node_id'),
            'description',
            'geom')
        }),
    )

    class Meta:
        model = Path
        fields = '__all__'

    class Media:
        js = (
            'poimap/js/path_admin_form.js',
            'bower_components/togeojson/togeojson.js',
        )

class POIAdminForm(forms.ModelForm):

    def clean_geom(self):
        """ Tricks to add default Z dimension into geometry """
        geom = self.cleaned_data["geom"]
        ogr = OGRGeometry(geom.wkt)
        ogr.coord_dim = 3
        return ogr.geos

    class Media:
        if "grappelli" in settings.INSTALLED_APPS:
            css = {
                "all": ('poimap/css/grp_poi_admin_form.css',),
            }
            js = (
                'poimap/js/grp_poi_admin_form.js',
            )
        else:
            css = {
                "all": ('poimap/css/poi_admin_form.css',),
            }
            js = (
                'poimap/js/poi_admin_form.js',
            )

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
                      ('zipcode', "city", 'country'))
        }),
        (None, {
            'classes': ('location',),
            'fields': ('geom',),
        }),
    )

admin.site.register(Area, AreaAdmin)
admin.site.register(Path, PathAdmin)
admin.site.register(POI, POIAdmin)
admin.site.register(POIType)
