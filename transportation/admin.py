from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from models import TimeSlot, Stop, Service, Line, RouteStop, Route, Travel, Bus, Customer, Order, Ticket, Connection
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
    search_fields = ('name',)
    list_filter = ('route',)

    inlines = [
        TimeSlotInlineAdmin
    ]

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

class TravelAdmin(admin.ModelAdmin):
    list_display = ("id", "stop1", "stop2", "distance", "price")
    list_editable = ("price",)

class BusAdminForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), widget=FilteredSelectMultiple("Service", is_stacked=False))

    class Meta:
        model = Bus
        fields = "__all__"

class BusAdmin(admin.ModelAdmin):
    list_display = ("name",)
    form = BusAdminForm


class TimeSlotInlineAdmin(admin.TabularInline):
    model = Ticket
    extra = 0
    can_delete = True

class OrderAdmin(admin.ModelAdmin):
    def ticket_number(self, obj):
        return obj.ticket_set.count()

    list_display = ("num", "ticket_number", "total_amount")
    inlines = [TimeSlotInlineAdmin]

class ConnectionInlineAdmin(admin.TabularInline):
    model = Connection
    can_delete = True

class TicketAdmin(admin.ModelAdmin):
    inlines = [ConnectionInlineAdmin]


admin.site.register(Customer)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Bus, BusAdmin)
admin.site.register(Line)
admin.site.register(Route, RouteAdmin)
admin.site.register(Stop, StopAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Travel, TravelAdmin)
