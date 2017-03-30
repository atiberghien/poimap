from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin

from models import Base, POIType, POIAddress, POI

class POIAddressInlineAdmin(LeafletGeoAdminMixin, admin.StackedInline):
    model = POIAddress
    extra = 1
    max_num = 1
    min_num = 1
    can_delete = False
    template = "admin/poi_stacked_inline.html"

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
            "all" : ('itinerary/css/itinerary_form_inline.css',),
        }
        js = (
            'itinerary/js/poi_form_inline.js',
        )

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
