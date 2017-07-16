from django.contrib import admin
from models import Fare, TimeSlot, Stop, Route, RunningDay, Line, LineStop
from leaflet.admin import LeafletGeoAdmin
from grappelli.forms import GrappelliSortableHiddenMixin
from poimap.admin import POIAdminForm
from .forms import StopForm

class TimeSlotInlineAdmin(admin.TabularInline):
    model = TimeSlot
    form = StopForm
    fields = ('stop', "hour")
    readonly_fields = ('stop',)
    extra = 0
    can_delete = False
    ordering = ("hour",)

    def has_add_permission(self, request):
        return False


class RouteAdmin(admin.ModelAdmin):
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


class LineStopInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = LineStop
    extra = 0
    sortable_field_name = "order"


class LineAdmin(admin.ModelAdmin):
    inlines = (LineStopInline,)


admin.site.register(Line, LineAdmin)
admin.site.register(Fare, FareAdmin)
admin.site.register(Stop, StopAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(RunningDay)
