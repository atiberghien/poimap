from django.contrib import admin
from django.contrib.gis import admin
from models import Hostings, PaymentType, OpeningDate, Contact, SleepingType, Sleeping

from leaflet.admin import LeafletGeoAdmin

# Register your models here.

class SleepingInlineAdmin(admin.TabularInline):
    model = Sleeping
    extra = 1

class ContactInlineAdmin(admin.TabularInline):
    model = Contact
    extra = 1


class HostingsAdmin(LeafletGeoAdmin):
    list_display = ['name',]
    inlines = (SleepingInlineAdmin, ContactInlineAdmin)


admin.site.register(Hostings, HostingsAdmin)
admin.site.register(PaymentType)
admin.site.register(OpeningDate)
admin.site.register(Contact)
admin.site.register(SleepingType)
admin.site.register(Sleeping)
