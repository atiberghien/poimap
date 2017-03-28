from django.contrib.gis import admin
from models import Base, POIType

# Register your models here.

admin.site.register(POIType)
admin.site.register(Base)
