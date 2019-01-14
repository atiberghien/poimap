# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.contrib.admin import SimpleListFilter

from leaflet.admin import LeafletGeoAdmin
from poimap.admin import POIAdminForm, POIMediaInline

from .models import TimeSlot, Stop, Service, Line, RouteStop, Route, Travel, Bus, Customer, Order, Ticket, Connection, PartnerSearch
from .forms import StopForm
import types
import csv

class TimeSlotInlineAdmin(admin.TabularInline):
    model = TimeSlot
    form = StopForm
    fields = ('stop', "hour", "is_next_day")
    readonly_fields = ('stop',)
    extra = 0
    can_delete = False
    ordering = ("order",)

    def has_add_permission(self, request):
        return False


class ServiceAdmin(admin.ModelAdmin):
    def bus_list(self, obj):
        bus_list = obj.bus_set.all().values_list('name', 'license_plate')
        bus_list = ", ".join(["%s (%s)" % (name, plate) for name, plate in bus_list])
        return bus_list
    bus_list.short_description = "Bus"

    list_display = ('slug', 'name', 'is_active', 'is_temporary', 'route', 'bus_list')
    search_fields = ('name',)
    list_editable = ('name', 'is_active', 'is_temporary')
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
    def line_list(self, obj):
        line_ids = list(obj.services.all().values_list("route__line", flat=True))
        lines = Line.objects.filter(id__in=set(line_ids))
        lines = ", ".join([l.name for l in lines])
        return lines
    line_list.short_description = "Line(s)"

    def service_list(self, obj):
        return ", ".join([s.name for s in obj.services.all()])
    service_list.short_description = "Services"

    list_display = ("name", "license_plate", "line_list", 'service_list')
    list_editable = ('license_plate', )
    form = BusAdminForm
    save_as = True

class TicketInlineAdmin(admin.TabularInline):

    model = Ticket
    extra = 0
    can_delete = True


def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_%s.csv"' % queryset.model.__name__.lower()
    writer = csv.writer(response)
    writer.writerow(modeladmin.csv_fields)
    for obj in queryset:
        row = []
        for field in modeladmin.csv_fields:
            if hasattr(obj, field):
                attr = getattr(obj, field)
                if isinstance(attr, types.MethodType):
                    attr = attr()
            if hasattr(modeladmin, field):
                attr = getattr(modeladmin, field)
                if isinstance(attr, types.MethodType):
                    attr = attr(obj)
            try:
                row.append(attr.encode("utf-8"))
            except:
                row.append(str(attr))
        writer.writerow(row)
    return response
export_as_csv.short_description = "Export CSV"


class paidOrderFilter(SimpleListFilter):
    title = 'Paiement'
    parameter_name = 'paid_at'
    
    def lookups(self, request, model_admin):
        return [("NOT_PAID", "Non Payée"), ("PAID", "Payée")]

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "NOT_PAID":
                return queryset.filter(paid_at__isnull=True)
            elif self.value() == "PAID":
                return queryset.filter(paid_at__isnull=False)                
        return queryset

class OrderAdmin(admin.ModelAdmin):

    def ticket_number(self, obj):
        return obj.ticket_set.count()
    
    def confirmation_link(self, obj):
        if obj.paid_at:
            return mark_safe("<a href='%s'>%s</a>" % (reverse('transportation-checkout-confirmation', args=[obj.num]), "Lien de confirmation"))
        return "-"

    list_display = ("num", 'customer', "ticket_number", "total_amount", "created_at", "paid_at", "source", "confirmation_link")
    csv_fields = ("num", "customer", "ticket_number", "source", "total_amount", "created_at", "paid_at")
    inlines = [TicketInlineAdmin]

    actions = [export_as_csv]
    list_filter = (paidOrderFilter, 'source')

class ConnectionInlineAdmin(admin.TabularInline):
    model = Connection
    can_delete = True

class TicketAdmin(admin.ModelAdmin):
    inlines = [ConnectionInlineAdmin]

class CustomerAdmin(admin.ModelAdmin):
    def order_count(self, obj):       
        return obj.order_set.filter(paid_at__isnull=False).count()

    list_display = ("last_name", "first_name", "email", "terms", "privacy", "optin", "order_count")
    search_fields = ("last_name", "first_name", "email")
    csv_fields = ("last_name", "first_name", "email", "terms", "privacy", "optin")
    actions = [export_as_csv]

class PartnerSearchAdmin(admin.ModelAdmin):

    list_display = ("search_date", "departure_stop", "arrival_stop", "travel_date", "partner", "info")
    list_filter = ("partner",)

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Bus, BusAdmin)
admin.site.register(Line)
admin.site.register(Route, RouteAdmin)
admin.site.register(Stop, StopAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Travel, TravelAdmin)
admin.site.register(PartnerSearch, PartnerSearchAdmin)
