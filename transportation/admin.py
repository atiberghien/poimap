from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from models import TimeSlot, Stop, Service, Line, RouteStop, Route, Travel, Bus, Customer, Order, Ticket, Connection, PartnerSearch
from leaflet.admin import LeafletGeoAdmin
from poimap.admin import POIAdminForm, POIMediaInline
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
    list_display = ('name', 'route')
    search_fields = ('name',)
    list_filter = ('route',)
    ordering = ("name",)
    
    inlines = [
        TimeSlotInlineAdmin
    ]

class StopAdminForm(POIAdminForm):
    class Meta(POIAdminForm.Meta):
        model = Stop

class StopAdmin(LeafletGeoAdmin):
    search_fields = ('name',)
    inlines = [POIMediaInline]
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


class RouteStopInline(admin.TabularInline):
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
    def line(self, obj):
        line_ids = list(obj.services.all().values_list("route__line", flat=True))
        lines = Line.objects.filter(id__in=set(line_ids))
        lines = ", ".join([l.name for l in lines])
        return lines

    line.short_description = "Line(s)"
    list_display = ("name", "line")
    form = BusAdminForm
    save_as = True


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
admin.site.register(PartnerSearch)
