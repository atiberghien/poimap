#-*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.gis import admin
from django.contrib.contenttypes.models import ContentType
try:
    from django.urls import reverse
except:
    from django.core.urlresolvers import reverse

from django.contrib.gis.gdal import OGRGeometry
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.admin.widgets import FilteredSelectMultiple
from adminsortable2.admin import SortableInlineAdminMixin
from django.utils.safestring import mark_safe
from ckeditor.widgets import CKEditorWidget
from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from treebeard.admin import TreeAdmin
from treebeard.forms import MoveNodeForm, movenodeform_factory

from .models import *

class CleanZDimensionMixin(object):
    def clean_geom(self):
        """ Tricks to add default Z dimension into geometry """
        geom = self.cleaned_data["geom"]
        ogr = OGRGeometry(geom.wkt)
        ogr.coord_dim = 3
        return ogr.geos

class OrderByDistanceMixin(object):
    def get_queryset(self, request):
        qs = super(OrderByDistanceMixin, self).get_queryset(request)
        qs = qs.annotate(distance=Distance('geom', Point(0, 90, srid=4326))).order_by('distance')
        return qs

class AreaAdminForm(CleanZDimensionMixin, forms.ModelForm):
    class Meta:
        model = Area
        fields = "__all__"

class AreaAdmin(LeafletGeoAdmin):
    list_display = ('name',)
    form = AreaAdminForm

    class Meta:
        model = Area
        fields = '__all__'

    class Media:
        if "grappelli" in settings.INSTALLED_APPS:
            pass
        else:
            js = (
                'poimap/js/path_admin_form.js',
                '@mapbox/togeojson/togeojson.js',
                'admin/js/jquery.init.js',
            )


class PathAdminForm(CleanZDimensionMixin, MoveNodeForm):

    class Meta:
        model = Path
        fields = "__all__"

class PathAdmin(LeafletGeoAdminMixin, TreeAdmin):
    form = movenodeform_factory(Path, form=PathAdminForm)
    list_display = ('name', 'slug')

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
            '@mapbox/togeojson/togeojson.js',
            'admin/js/jquery.init.js',
        )

class POIAdminForm(CleanZDimensionMixin, forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    types = forms.ModelMultipleChoiceField(queryset=POIType.objects.all(), widget=FilteredSelectMultiple("Types", is_stacked=False), required=False)
    
    class Media:
        if "grappelli" in settings.INSTALLED_APPS:
            css = {
                "all": ('poimap/css/grp_poi_admin_form.css',),
            }
            js = (
                'poimap/js/grp_poi_admin_form.js',
                'admin/js/jquery.init.js',
            )
        else:
            css = {
                "all": ('poimap/css/poi_admin_form.css',),
            }
            js = (
                'poimap/js/poi_admin_form.js',
                'admin/js/jquery.init.js',
            )

    class Meta:
        model = POI
        fields = "__all__"


class POIMediaInline(SortableInlineAdminMixin, admin.StackedInline):
    model = POIMedia
    extra = 2


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
            links += "Convertir en "
            link_list = []
            for child_model in POI.__subclasses__():
                link_list.append('<a href="%s">%s</a>' % (reverse("convert-poi", args=[obj.id, child_model._meta.model_name]),
                                                          child_model._meta.verbose_name.title()))
            links += ", ".join(link_list)

        return mark_safe(links)
    convert_actions.allow_tags = True
    convert_actions.short_description = ""

    list_display = ('id', 'name', 'type', "related_path", 'distance', "starred", 'convert_actions')
    list_editable = ('name', 'type', "related_path", "starred")
    list_filter = ('starred', 'type',)
    search_fields = ('name', 'slug')
    inlines = [POIMediaInline]
    form = POIAdminForm

    fieldsets = (
        (None, {
            'fields': (('name', 'type', 'related_path'), 'types', 'description')
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
        (None, {
            'fields': ('extra_data',),
        }),
    )


class POITypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'slug', 'icon', 'icon_file', 'color', 'get_typed_poi_count')
    list_editable = ('icon', )
    class Meta:
        model = POIType
        fields = '__all__'

admin.site.register(Area, AreaAdmin)
admin.site.register(Path, PathAdmin)
admin.site.register(POI, POIAdmin)
admin.site.register(POIType, POITypeAdmin)
admin.site.register(SpecificPOITypeTemplate)

