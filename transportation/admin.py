from django.contrib import admin
from models import Fare, TimeSlot, Stop, Service, RunningDay, Line, RouteStop, Route
from leaflet.admin import LeafletGeoAdmin
from poimap.admin import POIAdminForm
from grappelli.forms import GrappelliSortableHiddenMixin
from .forms import StopForm

class TimeSlotInlineAdmin(admin.TabularInline):
    model = TimeSlot
    form = StopForm
    fields = ('stop', "hour")
    readonly_fields = ('stop',)
    extra = 0
    can_delete = False
    ordering = ("order",)

    def has_add_permission(self, request):
        return False


class ServiceAdmin(admin.ModelAdmin):
    inlines = [
        TimeSlotInlineAdmin
    ]

class FareAdmin(admin.ModelAdmin):
    model = Fare
    list_display = ['type', 'price', 'valid_for', 'description']


class StopAdminForm(POIAdminForm):
    class Meta(POIAdminForm.Meta):
        model = Stop

class StopAdmin(LeafletGeoAdmin):
    search_fields = ('name',)

    form = StopAdminForm

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


class RouteStopInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = RouteStop
    extra = 0
    sortable_field_name = "order"


class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "line", "name", "direction", "path")
    list_editable = ("name", "direction", "path")
    inlines = (RouteStopInline,)


admin.site.register(Line)
admin.site.register(Route, RouteAdmin)
admin.site.register(Fare, FareAdmin)
admin.site.register(Stop, StopAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(RunningDay)
