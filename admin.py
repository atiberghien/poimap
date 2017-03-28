from django.contrib.gis import admin
from models import Base, POIType, POIAddress
from leaflet.admin import LeafletGeoAdmin


class POIAddressAdmin(LeafletGeoAdmin):
    fieldsets = (
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
            "all" : ('itinerary/css/itinerary_form.css',),
        }
        js = (
            'itinerary/js/poi_form.js',
        )


admin.site.register(POIAddress, POIAddressAdmin)
admin.site.register(POIType)
admin.site.register(Base)
