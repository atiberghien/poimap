from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from models import POIType, POI


class POIAdmin(LeafletGeoAdmin):
    list_display = ('id', 'name', 'type')
    list_editable = ('name', 'type')
    list_filter = ('type',)
    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': (('name', 'type'), 'description')
        }),
        (None, {
            'classes': ('address',),
            'fields': ('address',
                      ('zipcode', "city", 'country'),)
        }),
        (None, {
            'classes': ('location',),
            'fields': ('geom', ),
        }),
    )

    class Media:
        css = {
            "all": ('itinerary/css/itinerary_form.css',),
        }
        js = (
            'itinerary/js/poi_form.js',
        )


admin.site.register(POI, POIAdmin)
admin.site.register(POIType)
