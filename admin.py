from django.contrib.gis import admin
from models import Base, POIType, POIAddress
from leaflet.admin import LeafletGeoAdmin


class POIAddressAdmin(LeafletGeoAdmin):
    pass


admin.site.register(POIAddress, POIAddressAdmin)
admin.site.register(POIType)
admin.site.register(Base)
